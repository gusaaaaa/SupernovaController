class CodeTranslator:
    i2c_codes = {
        0 : "success",
        51 : "NACK_ERROR"
    }
    library = {
        "i2c" : i2c_codes
    }
    
    @staticmethod
    def get_message(protocol, code):
        protocol_dict = CodeTranslator.library.get(protocol)
        if protocol is None: return "Invalid Protocol"
        
        return protocol_dict.get(code, code)