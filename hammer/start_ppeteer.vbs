Set ws = CreateObject("Wscript.Shell")
ws.run "cmd /c ppeteer_producer.bat",0
ws.run "cmd /c ppeteer_receiver.bat",0