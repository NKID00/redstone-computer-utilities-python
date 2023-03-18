import redstone_computer_utilities as rcu

script = rcu.Script('test1')

@script.on_script_initialize()
def _():
    script.warn('test1 initialized!')

@script.on_interface_change('interface1')
def _(previous: int, current: int):
    script.info(f'gametime: {script.query_gametime()}')
    script.info(f'interface1 changed from {previous} to {current}')
    script.wait(rcu.second(1))
    script.info(f'gametime: {script.query_gametime()}')
    script.write_interface('interface2', script.read_interface('interface1'))

script.run()
