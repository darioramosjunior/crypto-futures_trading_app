from PyQt6.QtWidgets import QVBoxLayout, QWidget, QLabel, QHBoxLayout, QGraphicsSimpleTextItem
from database import Database
from PyQt6.QtCharts import QChart, QPieSeries, QChartView, QLineSeries, QValueAxis
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QBrush, QColor, QPainter, QFont, QPen


class AnalyticsTab(QWidget):

    def __init__(self, table_object, start_port):
        super().__init__()
        self.table_widget = table_object
        self.start_port = start_port
        self.trade_results = []
        self.win_count = 0
        self.lose_count = 0
        self.total_trades = 0
        self.fair_count = 0
        self.win_results = []
        self.lose_results = []
        self.fair_results = []
        self.win_rate = 0
        self.ave_gain = 0
        self.ave_loss = 0

        outer_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        self.setLayout(outer_layout)

        label1 = QLabel("This is Label 1")
        label2 = QLabel("This is Label 2")

        label3 = QLabel("""
        
        
        
        This is label 3
        This adad
        asdadad
        asdada
        
        
        
        """)
        label4 = QLabel("""
        
        
        
        
        This is Label 4
        
        
        
        
        
        """)

        self.get_statistics()

        pie_chart = PieChart(self.win_rate)
        self.equity_curve = EquityCurve(self.trade_results, self.start_port)

        left_layout.addWidget(pie_chart)
        left_layout.addWidget(label3)

        right_layout.addWidget(self.equity_curve)
        right_layout.addWidget(label4)

        outer_layout.addLayout(left_layout, 1)
        outer_layout.addLayout(right_layout, 2)

        self.show()

    def get_statistics(self):
        database = Database()
        database.cursor.execute("SELECT * FROM trades_results")
        trade_results = database.cursor.fetchall()

        if trade_results:
            number_of_trades = len(trade_results)
            self.total_trades = number_of_trades

            for each in trade_results:
                trade_result = each[2]
                self.trade_results.append(trade_result)
                if trade_result > 0.05:
                    self.win_results.append(trade_result)
                    self.win_count = self.win_count + 1
                elif trade_result < -0.05:
                    self.lose_results.append(trade_result)
                    self.lose_count = self.lose_count + 1
                else:
                    self.fair_results.append(trade_result)
                    self.fair_count = self.fair_count + 1

            self.win_rate = (self.win_count / (self.win_count + self.lose_count)) * 100
            self.ave_gain = sum(self.win_results) / len(self.win_results)
            self.ave_loss = sum(self.lose_results) / len(self.lose_results)

        print(self.win_rate, self.ave_gain, self.ave_loss)

    def update_start_port(self, start_port):
        self.equity_curve.load_equity_curve(start_port)


class PieChart(QWidget):
    def __init__(self, win_rate):
        super().__init__()
        layout = QVBoxLayout()
        self.win_rate = win_rate
        self.setLayout(layout)
        self.win_rate_string = "{:.2f}".format(self.win_rate)

        pie_chart = QChart()
        pie_chart.setTitle(f"Win Rate: {self.win_rate_string}%")
        title_font = QFont("Helvetica", 14)
        title_font.setBold(True)
        pie_chart.setTitleFont(title_font)
        pie_chart.legend().hide()

        # Set background color to dark gray
        background_brush = QBrush(QColor(70, 70, 70))
        pie_chart.setBackgroundBrush(background_brush)

        # Set title text color to white
        title_brush = QBrush(Qt.GlobalColor.white)
        pie_chart.setTitleBrush(title_brush)

        pie_series = QPieSeries()

        # Set color for the "Lose Rate" portion to gray
        lose_rate_slice = pie_series.append("Lose Rate", 1 - self.win_rate)
        lose_rate_slice.setColor(QColor(140, 140, 140))  # Dark Gray color

        # Set color for the "Win Rate" portion to green
        win_rate_slice = pie_series.append("Win Rate", self.win_rate)
        win_rate_slice.setColor(QColor(0, 220, 0))  # Green color

        pie_series.setHoleSize(0.4)
        pie_chart.addSeries(pie_series)

        pie_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        pie_chart_view = QChartView(pie_chart)
        pie_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        win_rate_text = QGraphicsSimpleTextItem("Hello!")
        win_rate_text.setFont(QFont("Arial", 14))

        layout.addWidget(pie_chart_view)


class EquityCurve(QWidget):
    def __init__(self, trade_results, start_port):
        super().__init__()
        self.trade_results = trade_results
        self.start_port = start_port

        # self.line_chart = QChart()
        # background_brush = QBrush(QColor(70, 70, 70))
        # self.line_chart.setBackgroundBrush(background_brush)
        #
        # self.line_chart_series = QLineSeries()
        # new_port = self.start_port
        # for index, each in enumerate(self.trade_results):
        #     self.line_chart_series.append(index, new_port)
        #     new_port = new_port + each
        #
        # self.line_chart.addSeries(self.line_chart_series)
        # self.line_chart.setTitle("Equity Curve")
        # self.line_chart.setTitleFont(QFont("Helvetica", 14))
        # self.line_chart.setTitleBrush(QBrush(QColor("gold")))
        # self.line_chart.legend().hide()
        # self.line_chart.setAnimationOptions(QChart.AnimationOption.GridAxisAnimations)
        #
        # # Set series color and pen properties for better visibility
        # pen = self.line_chart_series.pen()
        # pen.setColor(QColor("gold"))
        # self.line_chart_series.setPen(pen)
        #
        # # Create a y-axis and add it to the chart
        # y_axis = QValueAxis()
        # self.line_chart.addAxis(y_axis, Qt.AlignmentFlag.AlignLeft)
        # self.line_chart_series.attachAxis(y_axis)
        # y_axis.setLabelsColor(QColor("gold"))
        # y_axis.setGridLinePen(QPen(QColor("white"), 0.5, Qt.PenStyle.DashLine))
        #
        # chart_view = QChartView(self.line_chart)
        # chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_view = QChartView()

        self.chart_view = self.load_equity_curve(self.start_port)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(self.chart_view)

    def load_equity_curve(self, start_port):
        print("OH YEAH", start_port)
        line_chart = QChart()
        line_chart_series = QLineSeries()
        background_brush = QBrush(QColor(70, 70, 70))
        line_chart.setBackgroundBrush(background_brush)

        new_port = start_port
        for index, each in enumerate(self.trade_results):
            line_chart_series.append(index, new_port)
            new_port = new_port + each

        line_chart.addSeries(line_chart_series)
        line_chart.setTitle("Equity Curve")
        line_chart.setTitleFont(QFont("Helvetica", 12))
        line_chart.setTitleBrush(QBrush(QColor("gold")))
        line_chart.legend().hide()
        line_chart.setAnimationOptions(QChart.AnimationOption.GridAxisAnimations)

        # Set series color and pen properties for better visibility
        pen = line_chart_series.pen()
        pen.setColor(QColor("gold"))
        line_chart_series.setPen(pen)

        # Create a y-axis and add it to the chart
        y_axis = QValueAxis()
        line_chart.addAxis(y_axis, Qt.AlignmentFlag.AlignLeft)
        line_chart_series.attachAxis(y_axis)
        y_axis.setLabelsColor(QColor("gold"))
        y_axis.setGridLinePen(QPen(QColor("white"), 0.5, Qt.PenStyle.DashLine))

        chart_view = QChartView(line_chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        return chart_view


