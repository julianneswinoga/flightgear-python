#!/bin/bash
set -eu

base_dir='/tmp/fg-py-integration-test'
fg_exec="$base_dir/FlightGear-2020.3.19-x86_64.AppImage"
fg_root="$base_dir/fgdata"
fg_home="$base_dir/fghome"
fg_root_compressed="$base_dir/FlightGear-2020.3.19-data.txz"

mkdir -p "$base_dir"

if ! [ -f "$fg_exec" ]; then
    wget --output-document "$fg_exec" 'https://netactuate.dl.sourceforge.net/project/flightgear/release-2020.3/FlightGear-2020.3.19-x86_64.AppImage'
    chmod +x "$fg_exec"
fi
if ! [ -f "$fg_root_compressed" ]; then
    wget --output-document "$fg_root_compressed" 'https://netactuate.dl.sourceforge.net/project/flightgear/release-2020.3/FlightGear-2020.3.19-data.txz'
fi
if ! [ -d "$fg_root" ]; then
    # Don't add trailing slash to exclude
    # We need fgdata/AI/Aircraft/fallback_models.xml, but nothing else there
    tar \
        --exclude='fgdata/Aircraft/c172p' \
        --exclude='fgdata/Aircraft/Instruments' \
        --exclude='fgdata/Aircraft/Instruments-3d' \
        --exclude='fgdata/Scenery' \
        --exclude='fgdata/Textures/Terrain.winter' \
        --exclude='fgdata/AI/Aircraft/*[!xml]' \
        --exclude='fgdata/AI/Traffic' \
        --exclude='fgdata/Models' \
        --directory="$base_dir" \
        --checkpoint=20000 -x -f "$fg_root_compressed"
fi

# based on https://wiki.flightgear.org/Resource_Tracking_for_FlightGear#Startup_Profiles
fg_headless_opts=$(
cat << 'EOF'
--geometry=1x1
--disable-sound
--disable-terrasync
--disable-splash-screen
--fog-fastest
--disable-specular-highlight
--disable-random-objects
--disable-ai-models
--disable-clouds
--disable-clouds3d
--disable-distance-attenuation
--disable-real-weather-fetch
--disable-random-vegetation
--disable-random-buildings
--disable-horizon-effect
--prop:/sim/rendering/particles=0
--prop:/sim/rendering/multi-sample-buffers=1
--prop:/sim/rendering/multi-samples=2
--prop:/sim/rendering/draw-mask/clouds=false
--prop:/sim/rendering/draw-mask/aircraft=false
--prop:/sim/rendering/draw-mask/models=false
--prop:/sim/rendering/draw-mask/terrain=false
--prop:/sim/rendering/random-vegetation=0
--prop:/sim/rendering/random-buildings=0
--prop:/sim/ai/enabled=0
--prop:/sim/rendering/texture-compression=off
--prop:/sim/rendering/quality-level=0
--prop:/sim/rendering/shaders/quality-level=0
EOF
)

rm -r "$fg_home" || true
FG_HOME="$fg_home" timeout 600 "$fg_exec" --appimage-extract-and-run --fg-root="$fg_root" \
    --aircraft=ufo \
    --airport=ksfo \
    --fdm=null \
    --max-fps=30 \
    --httpd=8080 \
    --log-class=headless \
    --telnet=socket,bi,30,localhost,5500,tcp \
    --native-fdm=socket,out,30,localhost,5501,udp --native-fdm=socket,in,30,localhost,5502,udp \
    --native-ctrls=socket,out,30,localhost,5503,udp --native-ctrls=socket,in,30,localhost,5504,udp \
    --native-gui=socket,out,30,localhost,5505,udp --native-gui=socket,in,30,localhost,5506,udp \
    "$fg_headless_opts" &

fg_pid=$!
echo "FlightGear PID is $fg_pid"

http_timeout=1
udp_out_timeout=4
# Wait for FG to either die or come up
while true; do
  if ! ps -p $fg_pid > /dev/null; then
    echo "FlightGear($fg_pid) exited!"
    exit 1
  fi
  sleep 2

  set +e
  curl --silent --show-error --fail --connect-timeout $http_timeout 'http://localhost:8080/json/' >/dev/null 2>&1
  http_sts=$?

  nc -vz localhost 5500 >/dev/null 2>&1
  telnet_sts=$?

  timeout $udp_out_timeout socat -u UDP-RECVFROM:5501 SYSTEM:'head -c10'
  fdm_out_sts=$?
  nc -vzu localhost 5502 >/dev/null 2>&1
  fdm_in_sts=$?

  timeout $udp_out_timeout socat -u UDP-RECVFROM:5503 SYSTEM:'head -c10'
  ctrls_out_sts=$?
  nc -vzu localhost 5504 >/dev/null 2>&1
  ctrls_in_sts=$?

  timeout $udp_out_timeout socat -u UDP-RECVFROM:5505 SYSTEM:'head -c10'
  gui_out_sts=$?
  nc -vzu localhost 5506 >/dev/null 2>&1
  gui_in_sts=$?
  set -e

  if [[ $http_sts = 0 ]] \
     && [[ $telnet_sts = 0 ]] \
     && [[ $fdm_out_sts = 0 ]] \
     && [[ $fdm_in_sts = 0 ]] \
     && [[ $ctrls_out_sts = 0 ]] \
     && [[ $ctrls_in_sts = 0 ]] \
     && [[ $gui_out_sts = 0 ]] \
     && [[ $gui_in_sts = 0 ]]; then
    echo "FlightGear interfaces up!"
    break
  fi
  echo "Waiting for FlightGear($fg_pid)...http=$http_sts telnet=$telnet_sts "\
  "fdm_out=$fdm_out_sts fdm_in=$fdm_in_sts "\
  "ctrls_out=$ctrls_out_sts ctrls_in=$ctrls_in_sts "\
  "gui_out=$gui_out_sts gui_in=$gui_in_sts "
done

poetry run coverage run -m pytest -m 'fg_integration or not fg_integration' tests/

#read -p 'wait...'
kill "$fg_pid" || true
killall fgfs || true
