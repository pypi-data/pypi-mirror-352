pyguiEZ
=======

A lightweight, beginner-friendly GUI framework inspired by tkinter, built with pygame.

Example usage:

.. code-block:: python

    from pyguiEZ.app import App
    from pyguiEZ.label import Label
    from pyguiEZ.button import Button

    app = App("Demo")
    label = Label(app, "Hello", pos=(10, 10))

    def say_hi():
        label.set_text("Hi!")

    button = Button(app, "Click Me", pos=(10, 50), command=say_hi)
    app.run()
