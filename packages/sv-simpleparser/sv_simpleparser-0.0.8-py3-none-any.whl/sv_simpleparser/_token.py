from pygments.token import Token

__all__ = ["Module", "Port"]

# information about module
Module = Token.Module
ModuleName = Module.ModuleName

Module.Body.Instance.Module
Module.Body.Instance.Name
Module.Body.Instance.Connections

# information about ports
Port = Module.Port
PortDirection = Port.PortDirection
PortType = Port.PortType
PortWidth = Port.PortWidth
PortName = Port.Name
