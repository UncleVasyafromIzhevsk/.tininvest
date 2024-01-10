import matplotlib.pyplot as plt
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.garden.matplotlib import FigureCanvasKivyAgg

class MyApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        button = Button(text='Generate Plot')
        button.bind(on_press=self.generate_plot)
        layout.add_widget(button)
        return layout

    def generate_plot(self, instance):
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3, 4])
        canvas = FigureCanvasKivyAgg(fig)
        self.root.add_widget(canvas)

if __name__ == '__main__':
    MyApp().run()