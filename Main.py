import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Default Home Page
        self.home_url = "https://www.google.com"
        
        # Set up the browser widget
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(self.home_url))
        self.setCentralWidget(self.browser)
        self.showMaximized()
        
        # Create a navigation toolbar with Chrome-like styling
        navbar = QToolBar("Navigation")
        navbar.setIconSize(QSize(24, 24))
        navbar.setStyleSheet("""
            QToolBar {
                background: #f1f3f4;
                border: none;
                padding: 5px;
            }
            QToolButton {
                background: transparent;
                border: none;
                padding: 5px;
                margin: 0 2px;
            }
            QToolButton:hover {
                background-color: #e8eaed;
                border-radius: 4px;
            }
        """)
        self.addToolBar(navbar)
        
        # Back Button
        back_icon = self.style().standardIcon(QStyle.SP_ArrowBack)
        back_btn = QAction(back_icon, "", self)
        back_btn.triggered.connect(self.browser.back)
        back_btn.setToolTip("Back")
        navbar.addAction(back_btn)
        
        # Forward Button
        forward_icon = self.style().standardIcon(QStyle.SP_ArrowForward)
        forward_btn = QAction(forward_icon, "", self)
        forward_btn.triggered.connect(self.browser.forward)
        forward_btn.setToolTip("Forward")
        navbar.addAction(forward_btn)
        
        # Reload Button
        reload_icon = self.style().standardIcon(QStyle.SP_BrowserReload)
        reload_btn = QAction(reload_icon, "", self)
        reload_btn.triggered.connect(self.browser.reload)
        reload_btn.setToolTip("Reload")
        navbar.addAction(reload_btn)
        
        # Stop Button
        stop_icon = self.style().standardIcon(QStyle.SP_BrowserStop)
        stop_btn = QAction(stop_icon, "", self)
        stop_btn.triggered.connect(self.browser.stop)
        stop_btn.setToolTip("Stop")
        navbar.addAction(stop_btn)
        
        # Home Button
        home_icon = self.style().standardIcon(QStyle.SP_DirHomeIcon)  # Fixed icon
        home_btn = QAction(home_icon, "", self)
        home_btn.triggered.connect(self.navigate_home)
        home_btn.setToolTip("Home")
        navbar.addAction(home_btn)
        
        # URL Bar styled like Chrome's omnibox
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or enter address")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setStyleSheet("""
            QLineEdit {
                background: white;
                border: 1px solid #dcdcdc;
                padding: 6px;
                border-radius: 4px;
            }
        """)
        self.url_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        navbar.addWidget(self.url_bar)
        
        # Go Button with an icon (fallback to text if not found)
        go_icon = QIcon.fromTheme("media-playback-start")
        if go_icon.isNull():
            go_btn = QAction("Go", self)
        else:
            go_btn = QAction(go_icon, "", self)
        go_btn.triggered.connect(self.navigate_to_url)
        go_btn.setToolTip("Go")
        navbar.addAction(go_btn)
        
        # Status Bar with a progress bar for page loading
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.progress = QProgressBar()
        self.progress.setMaximumWidth(120)
        self.status.addPermanentWidget(self.progress)
        self.browser.loadProgress.connect(self.progress.setValue)
        
        # Update URL bar when URL changes
        self.browser.urlChanged.connect(self.update_url)
        
        # Update window title based on page title
        self.browser.titleChanged.connect(self.setWindowTitle)
        
        # Shortcut to focus the URL bar
        url_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        url_shortcut.activated.connect(self.focus_url_bar)

        # Set up the scraping dock widget for data extraction
        self.setup_scraping_dock()
    
    def setup_scraping_dock(self):
        """Set up a dock widget with tools for data scraping."""
        self.scraperDock = QDockWidget("Scraping Tools", self)
        self.scraperDock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        scraperWidget = QWidget()
        scraperLayout = QVBoxLayout()

        # CSS Selector input field
        self.selector_input = QLineEdit()
        self.selector_input.setPlaceholderText("Enter CSS selector")
        scraperLayout.addWidget(self.selector_input)

        # Button to scrape data using the CSS selector
        self.scrape_button = QPushButton("Scrape Data")
        self.scrape_button.clicked.connect(self.scrape_elements)
        scraperLayout.addWidget(self.scrape_button)

        # Button to view the full HTML source of the page
        self.view_source_button = QPushButton("View HTML Source")
        self.view_source_button.clicked.connect(self.view_source)
        scraperLayout.addWidget(self.view_source_button)

        # Output pane to display scraped data or HTML source
        self.scrape_output = QPlainTextEdit()
        self.scrape_output.setReadOnly(True)
        scraperLayout.addWidget(self.scrape_output)

        scraperWidget.setLayout(scraperLayout)
        self.scraperDock.setWidget(scraperWidget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.scraperDock)
    
    def navigate_home(self):
        self.browser.setUrl(QUrl(self.home_url))
    
    def navigate_to_url(self):
        url_text = self.url_bar.text().strip()
        if url_text:
            url = QUrl.fromUserInput(url_text)
            if url.isValid():
                self.browser.setUrl(url)
            else:
                QMessageBox.warning(self, "Invalid URL", "The URL you entered is not valid.")
    
    def update_url(self, qurl):
        self.url_bar.setText(qurl.toString())
    
    def focus_url_bar(self):
        self.url_bar.setFocus()

    def scrape_elements(self):
        """Scrape data from the current page using a CSS selector."""
        selector = self.selector_input.text().strip()
        if not selector:
            QMessageBox.warning(self, "No Selector", "Please enter a CSS selector.")
            return
        # Run JavaScript to get innerText of all matching elements
        js = f"Array.from(document.querySelectorAll('{selector}')).map(el => el.innerText)"
        self.browser.page().runJavaScript(js, self.display_scraped_data)

    def display_scraped_data(self, data):
        """Display the scraped data in the output pane."""
        if isinstance(data, list):
            output = "\n".join(data)
        else:
            output = str(data)
        self.scrape_output.setPlainText(output)

    def view_source(self):
        """Retrieve and display the full HTML source of the current page."""
        self.browser.page().toHtml(self.display_source)

    def display_source(self, html):
        self.scrape_output.setPlainText(html)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setApplicationName('Data Scraping Browser')
    window = MainWindow()
    sys.exit(app.exec_())
