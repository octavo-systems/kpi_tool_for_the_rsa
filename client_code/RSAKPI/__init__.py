from ._anvil_designer import RSAKPITemplate
from anvil import *
import anvil.server

class RSAKPI(RSAKPITemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def exit_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    return

  def sifter_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.server.call('GetRSASIFTER')
    return












