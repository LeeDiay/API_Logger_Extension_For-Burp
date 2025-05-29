#!/ Le Duc Anh - leducanh1503.works@gmail.com
# -*- coding: utf-8 -*-

from burp import IBurpExtender, IHttpListener, ITab
from javax.swing import JPanel, JScrollPane, JTable, JButton, JFileChooser
from javax.swing.table import DefaultTableModel
from javax.swing.event import TableModelListener, TableModelEvent
from javax.swing.filechooser import FileNameExtensionFilter
from java.awt import BorderLayout, FlowLayout
from java.util import ArrayList
from java.lang import Boolean
from java.net import URL
from java.io import File
import os
from datetime import datetime
import csv

class CustomTableModelListener(TableModelListener):
    def __init__(self, extender):
        self.extender = extender

    def tableChanged(self, e):
        if e.getType() == TableModelEvent.UPDATE:
            row = e.getFirstRow()
            col = e.getColumn()
            if col >= 4: 
                column_name = self.extender.columns[col]
                new_value = self.extender.table_model.getValueAt(row, col)
                self.extender.api_data[row][column_name] = new_value

class BurpExtender(IBurpExtender, IHttpListener, ITab):

    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName("API Logger Pro")
        callbacks.registerHttpListener(self)

        self.logged_requests = set()  # method + url key
        self.default_output_file = os.path.normpath("D:/Extension/Pentest_log.csv")  # Đường dẫn mặc định
        self.api_data = []  # Lưu trữ dữ liệu API và trạng thái checkbox
        self.columns = [
            "STT", "Date", "Method", "URL",
            "Missing level access control", "IDOR", "Privilege Escalation", "SQLi", "XSS",
            "CSRF", "Input Validation", "Sensitive Data Exposure",
            "No Resource Limit", "Other"
        ]
        self.csv_columns = [
            "STT", "Date", "Method", "URL", "Body",
            "Missing level access control", "IDOR", "Privilege Escalation", "SQLi", "XSS",
            "CSRF", "Input Validation", "Sensitive Data Exposure",
            "No Resource Limit", "Other"
        ]
        self.table_data = ArrayList()
        self.initGui()
        callbacks.addSuiteTab(self)

        try:
            # Chuẩn hóa đường dẫn để tránh lỗi Unicode
            self.default_output_file = self.default_output_file.encode('utf-8').decode('utf-8')
            print("Extension loaded successfully. API data will be saved to a user-selected location on export (default: {}).".format(self.default_output_file))
        except Exception as e:
            print("Error initializing extension: {}".format(str(e)))
            raise

    def initGui(self):
        self.panel = JPanel()
        self.panel.setLayout(BorderLayout())

        # Tạo table model
        self.table_model = DefaultTableModel(self.table_data, self.columns)
        self.table = JTable(self.table_model)

        # Đặt kiểu dữ liệu cho các cột checkbox
        for i in range(4, len(self.columns)):  
            self.table.getColumnModel().getColumn(i).setCellEditor(self.table.getDefaultEditor(Boolean))
            self.table.getColumnModel().getColumn(i).setCellRenderer(self.table.getDefaultRenderer(Boolean))

        # Thêm listener để đồng bộ checkbox với api_data
        self.table_model.addTableModelListener(CustomTableModelListener(self))

        scrollPane = JScrollPane(self.table)

        # Thêm các nút Export Report, Load CSV, Clear All, căn giữa
        button_panel = JPanel()
        button_panel.setLayout(FlowLayout(FlowLayout.CENTER))
        export_button = JButton("Export Report", actionPerformed=self.exportReport)
        load_button = JButton("Load CSV", actionPerformed=self.loadCSV)
        clear_button = JButton("Clear All", actionPerformed=self.clearAll)
        clear_selected_button = JButton("Clear Selected", actionPerformed=self.clearSelected)  # Thêm nút mới
        button_panel.add(export_button)
        button_panel.add(load_button)
        button_panel.add(clear_button)
        button_panel.add(clear_selected_button)  # Thêm vào panel

        # Thêm các thành phần vào panel
        self.panel.add(scrollPane, BorderLayout.CENTER)
        self.panel.add(button_panel, BorderLayout.SOUTH)

    def getTabCaption(self):
        return "API Logger"

    def getUiComponent(self):
        return self.panel

    def loadCSV(self, event):
        try:
            # Tạo JFileChooser để chọn file CSV
            file_chooser = JFileChooser()
            file_chooser.setFileFilter(FileNameExtensionFilter("CSV Files", ["csv"]))
            result = file_chooser.showOpenDialog(self.panel)

            if result == JFileChooser.APPROVE_OPTION:
                input_file = file_chooser.getSelectedFile().getAbsolutePath()
                
                # Xóa dữ liệu hiện có
                self.api_data = []
                self.logged_requests.clear()
                while self.table_model.getRowCount() > 0:
                    self.table_model.removeRow(0)

                with open(input_file, 'r') as f:
                    reader = csv.DictReader(f)
                    if reader.fieldnames != self.csv_columns:
                        print("Error loading CSV: Invalid column structure. Expected columns: {}".format(self.csv_columns))
                        return

                    for row in reader:
                        stt = int(row["STT"])
                        timestamp = row["Date"]
                        method = row["Method"]
                        url_path = row["URL"]
                        body = row["Body"]

                        # Chuyển giá trị checkbox từ OK/Not Pass/N/A thành True/False
                        data = {
                            "STT": stt,
                            "Timestamp": timestamp,
                            "Method": method,
                            "URL": url_path,
                            "Body": body,
                            "Missing level access control": row["Missing level access control"] == "OK",
                            "IDOR": row["IDOR"] == "OK",
                            "Privilege Escalation": row["Privilege Escalation"] == "OK",
                            "SQLi": row["SQLi"] == "OK",
                            "XSS": row["XSS"] == "OK",
                            "CSRF": row["CSRF"] == "OK",
                            "Input Validation": row["Input Validation"] == "OK",
                            "Sensitive Data Exposure": row["Sensitive Data Exposure"] == "N/A",
                            "No Resource Limit": row["No Resource Limit"] == "N/A",
                            "Other": row["Other"] == "N/A"
                        }
                        self.api_data.append(data)
                        self.logged_requests.add(method + url_path)

                        # Thêm vào bảng GUI
                        gui_row = [
                            stt, timestamp, method, url_path,
                            data["Missing level access control"],
                            data["IDOR"],
                            data["Privilege Escalation"],
                            data["SQLi"],
                            data["XSS"],
                            data["CSRF"],
                            data["Input Validation"],
                            data["Sensitive Data Exposure"],
                            data["No Resource Limit"],
                            data["Other"]
                        ]
                        self.table_model.addRow(gui_row)

                print("CSV loaded successfully from {} at {}".format(input_file, datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
            else:
                print("Load CSV cancelled by user at {}".format(datetime.now().strftime('%d/%m/%Y %H:%M:%S')))

        except Exception as e:
            print("Error loading CSV: {}".format(str(e)))
            if "codec" in str(e).lower():
                print("Possible encoding issue with file path. Ensure path uses valid UTF-8 characters.")

    def exportReport(self, event):
        try:
            # Tạo JFileChooser để chọn nơi lưu file
            file_chooser = JFileChooser()
            file_chooser.setSelectedFile(File("Pentest_log.csv"))  # Tên file mặc định
            file_chooser.setFileFilter(FileNameExtensionFilter("CSV Files", ["csv"]))
            result = file_chooser.showSaveDialog(self.panel)

            if result == JFileChooser.APPROVE_OPTION:
                output_file = file_chooser.getSelectedFile().getAbsolutePath()
                # Đảm bảo file có đuôi .csv
                if not output_file.lower().endswith(".csv"):
                    output_file += ".csv"

                # Sắp xếp api_data theo URL và cập nhật STT
                sorted_data = sorted(self.api_data, key=lambda x: x["URL"])
                for index, data in enumerate(sorted_data, start=1):
                    data["STT"] = index

                with open(output_file, 'w') as f: 
                    writer = csv.writer(f)
                    writer.writerow(self.csv_columns)
                    for data in sorted_data:
                        row = [
                            data["STT"],
                            data["Timestamp"],
                            data["Method"],
                            data["URL"],
                            data["Body"],
                            "OK" if data["Missing level access control"] else "Not Pass",
                            "OK" if data["IDOR"] else "Not Pass",
                            "OK" if data["Privilege Escalation"] else "Not Pass",
                            "OK" if data["SQLi"] else "Not Pass",
                            "OK" if data["XSS"] else "Not Pass",
                            "OK" if data["CSRF"] else "Not Pass",
                            "OK" if data["Input Validation"] else "Not Pass",
                            "N/A" if data["Sensitive Data Exposure"] else "Not Pass",
                            "N/A" if data["No Resource Limit"] else "Not Pass",
                            "N/A" if data["Other"] else "Not Pass"
                        ]
                        writer.writerow(row)
                print("Report exported successfully to {} at {}".format(output_file, datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
            else:
                print("Export cancelled by user at {}".format(datetime.now().strftime('%d/%m/%Y %H:%M:%S')))

        except Exception as e:
            print("Error exporting report: {}".format(str(e)))
            if "codec" in str(e).lower():
                print("Possible encoding issue with file path. Ensure path uses valid UTF-8 characters.")

    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):
        if toolFlag == self._callbacks.TOOL_REPEATER and messageIsRequest:
            try:
                httpService = messageInfo.getHttpService()
                request = messageInfo.getRequest()
                requestInfo = self._helpers.analyzeRequest(httpService, request)

                method = requestInfo.getMethod()
                url_obj = requestInfo.getUrl()  # URL object
                url_path = URL(str(url_obj)).getPath() or "/"  # Lấy path, mặc định "/" nếu rỗng
                key = method + url_path

                if key in self.logged_requests:
                    return

                self.logged_requests.add(key)
                body = request[requestInfo.getBodyOffset():].tostring()
                timestamp = datetime.now().strftime('%d/%m/%Y')  # Định dạng dd/mm/YYYY
                stt = len(self.api_data) + 1  # STT tăng dần từ 1

                # Lưu dữ liệu vào api_data
                data = {
                    "STT": stt,
                    "Timestamp": timestamp,
                    "Method": method,
                    "URL": url_path,
                    "Body": body,
                    "Missing level access control": True,
                    "IDOR": True,
                    "Privilege Escalation": True,
                    "SQLi": True,
                    "XSS": True,
                    "CSRF": True,
                    "Input Validation": True,
                    "Sensitive Data Exposure": True,
                    "No Resource Limit": True,
                    "Other": True
                }
                self.api_data.append(data)

                # Thêm vào bảng GUI
                row = [
                    stt, timestamp, method, url_path,
                    True, True, True, True, True,
                    True, True, True, True, True
                ]
                self.table_model.addRow(row)
                print("Logged API: {} ({})".format(url_path, method))

            except Exception as e:
                print("Error processing HTTP message: {}".format(str(e)))
                if "codec" in str(e).lower():
                    print("Possible encoding issue with URL or file path. Ensure all paths use valid UTF-8 characters.")
                raise

    def clearAll(self, event):
        """
        Xóa toàn bộ dữ liệu khỏi bảng và bộ nhớ.
        """
        self.api_data = []
        self.logged_requests.clear()
        while self.table_model.getRowCount() > 0:
            self.table_model.removeRow(0)
        print("All data cleared at {}".format(datetime.now().strftime('%d/%m/%Y %H:%M:%S')))

    def clearSelected(self, event):
        """
        Xóa dòng được chọn khỏi bảng và api_data.
        """
        selected_row = self.table.getSelectedRow()
        if selected_row == -1:
            print("No row selected to clear.")
            return
        # Xóa khỏi api_data
        if 0 <= selected_row < len(self.api_data):
            removed = self.api_data.pop(selected_row)
            key = removed["Method"] + removed["URL"]
            self.logged_requests.discard(key)
        # Xóa khỏi bảng
        self.table_model.removeRow(selected_row)
        print("Selected row cleared at {}".format(datetime.now().strftime('%d/%m/%Y %H:%M:%S')))