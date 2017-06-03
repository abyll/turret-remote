from kivy.app import App
from kivy.lang import Builder

root = Builder.load_string('''
FloatLayout:
    AnchorLayout:
        anchor_x: 'right'
        anchor_y: 'bottom'

        Button:
            text: 'Hello World'
            size: 100, 100
            size_hint: None, None

    AnchorLayout:
        anchor_x: 'left'
        anchor_y: 'center'

        Label:
            text: 'Am i a Label ?'
            size: 100, 100
            size_hint: None, None
''')

class MyJB(App):
    def build(self):
        return root

if __name__ == '__main__':
    MyJB().run()