from calendar import HTMLCalendar


class Calendar(HTMLCalendar):
    def __init__(self, year: int, month: int) -> None:
        self.year = year
        self.month = month
        super(Calendar, self).__init__()

    def formatday(self, day: int, weekday: int) -> str:
        """
        Return a day as a table cell with Bootstrap classes.
        """
        if day != 0:
            return f'<td><a href="#">{day}</a></td>'
        return "<td></td>"

    def formatweek_month(self, theweek: list[tuple[int, int]]) -> str:
        """
        Return a complete week as a table row.
        """
        week_html = ""
        for d, weekday in theweek:
            week_html += self.formatday(d, weekday)
        return f"""<tr scope="row" style="height: 120px;">
                        {week_html}
                   </tr>"""

    def heading_with_options(self) -> str:
        """
        Return the heading of the calendar with options to go to the previous and next month.
        """
        next_month = self.month + 1
        if next_month > 12:
            next_month = 1
            next_year = self.year + 1
        else:
            next_year = self.year
        previous_month = self.month - 1
        if previous_month < 1:
            previous_month = 12
            previous_year = self.year - 1
        else:
            previous_year = self.year
        return f"""<p class="h3 mb-2">{self.formatmonthname(self.year, self.month)}</p>
                    <div class="d-flex">
                        <a class="btn btn-sm btn-primary me-2" href="?month={next_month}&year={next_year}">Vorheriger Monat</a>
                        <a class="btn btn-sm btn-primary me-2" href="?month={previous_month}&year={previous_year}">Nächster Monat</a>
                        <a class="btn btn-sm btn-primary" href="">Neue Reservierung</a>
                    </div>"""

    def formatmonth(self, theyear: int = 1, themonth: int = 1, withyear: bool = True) -> str:
        """
        Return a formatted month as a table.
        """
        weeks_html = ""
        for week in self.monthdays2calendar(self.year, self.month):
            weeks_html += self.formatweek_month(week)
        return f"""{self.heading_with_options()}
                    <table class="table table-striped">
                        <thead>
                            <tr scope="row">
                                {self.formatweekheader()}
                            </tr>
                        </thead>
                        <tbody>
                            {weeks_html}
                        </tbody>
                    </table>"""
