def UiWindow(title, icon, content, cheight=10, cwidth=15):
    return {
        "widgettype":"PopupWindow",
        "options":{
            "author":"cc",
            "cwidth":cwidth,
            "cheight":cheight,
            "title":title,
            "content":content,
            "icon":icon or entire_url('/bricks/imgs/app.png'),
            "movable":True,
            "auto_open":True
        }
    }

def UiError(title="出错", message="出错啦", timeout=5):
    return {
        "widgettype":"Error",
        "options":{
            "author":"tr",
            "timeout":timeout,
            "cwidth":15,
            "cheight":10,
            "title":title,
            "message":message
        }
    }

def UiMessage(title="消息", message="后台消息", timeout=5):
    return {
        "widgettype":"Message",
        "options":{
            "author":"tr",
            "timeout":timeout,
            "cwidth":15,
            "cheight":10,
            "title":title,
            "message":message
        }
    }

def load_pybricks():
	g = ServerEnv()
	g.UiWindow = UiWindow
	g.UiError = UiError
	g.UiMessage = UiMessage

