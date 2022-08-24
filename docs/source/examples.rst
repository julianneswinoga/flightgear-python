Examples
========

Simple FDM loop
---------------

.. literalinclude:: /../../examples/simple_fdm.py
    :caption: examples/simple_fdm.py
    :lines: 2-

Simple telnet (properties) interface
------------------------------------

.. literalinclude:: /../../examples/simple_telnet.py
    :caption: examples/simple_telnet.py
    :lines: 2-

.. raw:: html

   <details>
   <summary><a>sample output</a></summary>

.. code-block:: text

    {'directories': ['/sim',
                     '/position',
                     '/orientation',
                     '/autopilot',
                     '/velocities',
                     '/controls',
                     '/environment',
                     '/instrumentation',
                     '/local-weather',
                     '/accelerations',
                     '/devices',
                     '/input',
                     '/systems',
                     '/logging',
                     '/nasal',
                     '/scenery',
                     '/earthview',
                     '/fdm',
                     '/engines',
                     '/payload',
                     '/aircraft',
                     '/consumables',
                     '/gear',
                     '/rotors',
                     '/limits',
                     '/save',
                     '/command',
                     '/canvas',
                     '/surface-positions',
                     '/ai',
                     '/rendering',
                     '/ephemeris',
                     '/pax',
                     '/io',
                     '/hazards',
                     '/Interior',
                     '/_debug'],
     'properties': {'/models': ''}}
    Altitude: 4757.3ft
    Altitude: 4782.7ft
    Altitude: 4807.4ft
    ...

.. raw:: html

   </details>
