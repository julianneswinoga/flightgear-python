Quick-Start
===========

#. Install via ``pip``: ``pip3 install flightgear-python``
#. Write python code. See :ref:`Simple FDM loop`
#. Start FlightGear with the right options:

    #. If you're using the FDM interface:

        * ``--fdm=null --max-fps=30 --native-fdm=socket,out,30,,5501,udp --native-fdm=socket,in,30,,5502,udp``

        * the ``30`` in the arguments must match, so that the IO and the framerate are the same

    #. If you're using the telnet (properties) interface:

        * ``--telnet=socket,bi,60,localhost,5500,tcp``

        * The ``60`` is how fast FG will check the telnet connection (I think)

#. Run your python code!
