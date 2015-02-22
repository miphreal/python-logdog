# == POLLER ==  # periodically getting and forwarding data
# def poll():  -- active polling
#   while True:
#       self.on_recv(input.pop())
# def on_recv(data):  -- passive waiting for messages
#   output.on_recv(data)

# == COLLECTOR ==  # waiting for data and collecting
# def on_recv(data):
#   (storage|buffer).put(data)
# def pop():
#   return (storage|buffer).pop()

# == PROCESSOR ==  # accepting data, processing and forwarding
# def on_recv(data):
#   .. process data
#   output.on_recv(data)

# == CONNECTOR(SENDER, RECEIVER) ==  # transfer messages over network
# def SENDER.on_recv(data):
#   <socket>.send(data)
# def RECEIVER.on_recv(data):
#   output.on_recv(data)

# == VIEWER ==  # accepting data and displaying it
# def on_recv(data):
#   .. show some representation of data
