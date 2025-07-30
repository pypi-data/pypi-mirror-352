
import gradio as gr
from gradio_myfirstcomponent import MyFirstComponent


example = MyFirstComponent().example_value()

demo = gr.Interface(
    lambda x:x,
    MyFirstComponent(),  # interactive version of your component
    MyFirstComponent(),  # static version of your component
    # examples=[[example]],  # uncomment this line to view the "example version" of your component
)


if __name__ == "__main__":
    demo.launch()
