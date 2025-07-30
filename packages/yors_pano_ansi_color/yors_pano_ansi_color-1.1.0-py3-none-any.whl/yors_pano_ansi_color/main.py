
# feat(core): def class to label ansi color
class AnsiColor:
  END = '\33[0m'
  BOLD = '\33[1m'
  ITALIC = '\33[3m'
  UNDERLINE = '\33[4m'
  BLINK = '\33[5m'
  BLINK2 = '\33[6m'
  SELECTED = '\33[7m'

  BLACK = '\33[30m'
  RED = '\33[31m'
  GREEN = '\33[32m'
  YELLOW = '\33[33m'
  BLUE = '\33[34m'
  VIOLET = '\33[35m'
  BEIGE = '\33[36m'
  WHITE = '\33[37m'

  BLACKBG = '\33[40m'
  REDBG = '\33[41m'
  GREENBG = '\33[42m'
  YELLOWBG = '\33[43m'
  BLUEBG = '\33[44m'
  VIOLETBG = '\33[45m'
  BEIGEBG = '\33[46m'
  WHITEBG = '\33[47m'

  GREY = '\33[90m'
  LIGHTRED = '\33[91m'
  LIGHTGREEN = '\33[92m'
  LIGHTYELLOW = '\33[93m'
  LIGHTBLUE = '\33[94m'
  LIGHTVIOLET = '\33[95m'
  LIGHTBEIGE = '\33[96m'
  LIGHTWHITE = '\33[97m'

  GREYBG = '\33[100m'
  LIGHTREDBG = '\33[101m'
  LIGHTGREENBG = '\33[102m'
  LIGHTYELLOWBG = '\33[103m'
  LIGHTBLUEBG = '\33[104m'
  LIGHTVIOLETBG = '\33[105m'
  LIGHTBEIGEBG = '\33[106m'
  LIGHTWHITEBG = '\33[107m'

# feat(core): def func to log msg
def log_msg(s):
  print(f"{AnsiColor.GREEN}{s} {AnsiColor.END}")
# feat(core): def func to log error
def log_error(s):
  print(f"{AnsiColor.RED}{s} {AnsiColor.END}")
# feat(core): def func to log warn
def log_warn(s):
  print(f"{AnsiColor.BLUE}{s} {AnsiColor.END}")

# log_msg(f"[pano] hi, zero! this is pano.")
# log_warn(f"[pano] hi, zero! this is pano.")
# log_error(f"[pano] hi, zero! this is pano.")

def info_status(msg_body, status):
    msg_success = "✅"
    msg_failed = "❌"
    msg_warn = "ℹ️"

    if status == 0:
        print(f"{msg_success} {msg_body}")
    elif status == 1:
        print(f"{msg_failed} {msg_body}")
    else:
        print(f"{msg_warn} {msg_body}")


def msg_padd(msg, msg_max_len):
    msg_len = len(msg)
    msg_fill_length = (msg_max_len - msg_len + 2) // 2
    msg_padding = '-' * msg_fill_length
    padded_msg = f"{msg_padding}-{msg}-{msg_padding}"
    return padded_msg[:msg_max_len]

def info_step(msg):
    print(msg_padd(msg, 60))