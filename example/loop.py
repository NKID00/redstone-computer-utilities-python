import redstone_computer_utilities as rcu

script = rcu.Script('loop')

@script.on_interface_change('interface1')
def _(previous: int, current: int):
    for _ in range(100):
        script.write_interface('interface2', script.query_gametime() % 16)
        script.wait(rcu.gametick(1))

script.run()
