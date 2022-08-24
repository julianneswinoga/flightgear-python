Quick-Start
===========

1. Install via ``pip``: ``pip3 install flightgear-python``
2. Write python code. See :ref:`Simple FDM loop`
3. Start FlightGear with the following options: ``--fdm=null --max-fps=30 --native-fdm=socket,out,30,,5501,udp --native-fdm=socket,in,30,,5502,udp``

  a. the ``30`` in the arguments must match, so that the IO and the framerate are the same

3. Run your python code!
