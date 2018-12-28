import picard

@picard.file('hello.o', 'hello.c')
async def hello_o(target, context, hello_c):
    cc = context.config.get('CC', 'cc')
    cpp_flags = context.config.get('CPPFLAGS', None)
    c_flags = context.config.get('CFLAGS', None)
    await picard.sh(cc, cpp_flags, c_flags, '-c', hello_c)

@picard.file('hello', hello_o)
async def hello(target, context, hello_o):
    cc = context.config.get('CC', 'cc')
    ld_flags = context.config.get('LDFLAGS', None)
    ld_libs = context.config.get('LDLIBS', None)
    await picard.sh(cc, ld_flags, '-o', 'hello', hello_o, ld_libs)

if __name__ == '__main__':
    picard.make(hello)
