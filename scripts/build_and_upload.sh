#!/bin/bash
set -e

trap 'catch $? $LINENO' EXIT
function catch {
    if [ "$1" != "0" ]; then
        # error handling goes here
        echo "Caught error $1 occurred LN:$2"
        if [ -n "$release_tag" ]; then
            echo "Rolling back tag $release_tag"
            git tag -d "$release_tag" || true
            git push --delete origin "$release_tag" || true
        fi
    fi
}

if [[ $(git diff --stat) != '' ]]; then
    echo 'Dirty repo! Not building'
    exit 1
fi

rm -r ./dist/*.{tar.gz,whl}
rmdir dist # Should fail if extra files are in dist
./.venv/bin/python3 -m build
pkg_ver=$(./.venv/bin/python3 -c 'from pkginfo import Wheel;import glob;print(Wheel(glob.glob("./dist/*.whl")[0]).version)')
release_tag="release-$pkg_ver"
echo "Package version is $pkg_ver"
git tag -a "$release_tag" -m "auto-tag release $pkg_ver"
git push origin --tags
./.venv/bin/python3 -m twine upload dist/*
