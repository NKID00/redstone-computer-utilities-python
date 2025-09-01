from redstone_computer_utilities import Script

script = Script('hello')

@script.on_init()
def init(ctx):
    ctx.info('on_init is called!')

@script.on_execute()
def execute(ctx, arguments):
    ctx.info('on_execute is called!')
    ctx.info(f'gametime = {ctx.query_gametime()}')
    return 1

script.run(logger=True)
