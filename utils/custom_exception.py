import traceback
import sys

class CustomException(Exception):

    def __init__(self, error_message, erro_datail:sys):
        super().__init__(error_message)
        self.error_message = self.get_detailed_error_message(error_message, erro_datail)


    @staticmethod
    def get_detailed_error_message(erro_message, erro_detail:sys):
        #Obtendo o tipo de exceção, o valor e traceback
        _,_, exc_tb = traceback.sys.exc_info()
        file_name = exc_tb.tb_frame.f_code.co_filename
        line_number = exc_tb.tb_lineno

        #capturar o traceback completo
        tb_str = "". join(traceback.format_exception(*sys.exc_info()))

        #Incluindo o traceback completo na mensagem
        return f"Error in {file_name}, line {line_number}: {erro_message} \n\n Original Traceback:\n{tb_str}"

    def __str__(self):
        return self.error_message