import redstone_computer_utilities as rcu


script = rcu.Script('main')

def calc_expected_result(test_case):
    return test_case * 16


@script.on_script_run()
def _(args):
    for test_case in range(256):
        target.write(test_case)
        script.wait(rcu.redstonetick(2))
        expected = calc_expected_result(test_case)
        real = result.read()
        if expected != real:
            print(f'Test case failed: expect {expected}, got {real}')


script.run()
