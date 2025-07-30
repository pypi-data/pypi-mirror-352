import argparse
import os

print(os.getcwd())

os.environ["KIVY_NO_ARGS"] = "1"

parser = argparse.ArgumentParser(description='Shoggoth Card Creator')
parser.add_argument('-v', '--view', metavar='FILE', help='Open in viewer mode with specified file')
args = parser.parse_args()


print('works')
if args.view:
    # Start in viewer mode
    print('works')
    from shoggoth.viewer import ViewerApp
    app = ViewerApp(args.view)
else:
    # Start in normal mode
    from shoggoth.main import ShoggothApp
    print('works')
    app = ShoggothApp()
print('works')
app.run()
