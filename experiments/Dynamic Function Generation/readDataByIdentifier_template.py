"""This file is an experiment and should not be used for any serious coding"""

read_data_by_identifier_requests = {}
read_data_by_identifier_responses = {}


# example content of the read_data_by_identifier function
def read_data_by_identifier(diagnosticIdentifier):

    response = None
    # get the payload
    output = read_data_by_identifier_requests[diagnosticIdentifier]

    # send the uds request
    # uds.send(output)

    # get the response
    # response = uds.recv()

    # check the response
    decodeFunc = read_data_by_identifier_responses[diagnosticIdentifier]

    return decodeFunc(response)



# function template for checking the response
check_rdbiPayload_template = str(
    "def check_{0}(payload):\n"
    "    from uds import DecodeFunctions\n"
    "    expectedLength = {1}\n"
    "    if(len(payload) != expectedLength):\n"
    '        raise Exception("Unexpected length of response: Received length: " '
    ' + str(len(payload)) + " Payload: " + str(payload) )\n\n'
    "    positiveResponse = {2}\n"
    "    negative_response = {3}\n\n"
    "    responseReceived = payload[0]\n\n"
    "    if(responseReceived == positiveResponse):\n"
    "        diagnosticIdentifier_expected = {4}\n"
    "        diagnosticIdentifier_received = "
    "DecodeFunctions.build_int_from_list(payload[1:3])\n\n"
    "        if(diagnosticIdentifier_expected != diagnosticIdentifier_received):\n"
    '            raise Exception("Diagnostic identifier does not match expected response: '
    'Payload: " + str(payload))\n'
    "        return None\n"
    "    elif(responseReceived == negative_response):\n"
    '       raise Exception("Negative response received: Payload: " + str(payload))\n'
    "    else:\n"
    '        raise Exception("Unexpected response: Payload: " + str(payload))'
).format("Boot_Software_Identification_Read", 28, 0x62, 0x7F, 0xF180)


# function template for decoding the response and presenting it to the user
decode_rdbiPayload_template = str(
    "def decode_{0}(payload):\n"
    "    from uds import DecodeFunctions\n"
    "    check_{0}(payload)\n"
    "    numberOfModules = payload[3:4]\n"  # these two lines need to be dynamically populated based on the content
    "    Boot_Software_Identification = payload[4:28]\n"  # these two lines need to be dynamically populated based on the content
    "    result = {{}}\n"
    "    result['numberOfModules'] = numberOfModules[0]\n"  # these two lines need to be dynamically populated based on the content
    "    result['Boot Software Identification'] = DecodeFunctions.int_list_to_string(Boot_Software_Identification, 'ISO-8859-1')\n"  # these two lines need to be dynamically populated based on the content
    "    return result"
).format("Boot_Software_Identification_Read")

exec(check_rdbiPayload_template)
exec(decode_rdbiPayload_template)

testVal_correct = [
    0x62,
    0xF1,
    0x80,
    0x03,
    0x30,
    0x30,
    0x30,
    0x30,
    0x30,
    0x30,
    0x30,
    0x30,
    0x30,
    0x30,
    0x30,
    0x30,
    0x30,
    0x30,
    0x30,
    0x30,
    0x30,
    0x30,
    0x30,
    0x30,
    0x30,
    0x30,
    0x30,
    0x37,
]

print(decode_Boot_Software_Identification_Read(testVal_correct))
