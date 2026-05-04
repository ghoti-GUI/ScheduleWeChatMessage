from viewmodels.main_viewmodel import MainViewModel
from views.main_view import MainView

if __name__ == "__main__":
    viewmodel = MainViewModel()
    viewmodel.init_app()

    app = MainView(viewmodel)
    app.run()
