from dashgen.core.components import render_card, render_table, render_chart

class Column:
    def __init__(self, width=12):
        self.width = width
        self.content = []
        self._types = []
        self._chart_heights = []

    def add_card(self, title, value, target, currency="R$", style=None):
        self.content.append(render_card(title, value, target, style=style, currency=currency))
        self._types.append("card")
        return self

    def add_table(self, title, data, headers, progress_columns=None, progress_config=None):
        self.content.append(render_table(title, data, headers, progress_columns=progress_columns, progress_config=progress_config))
        self._types.append("table")
        return self

    def add_chart(self, chart_type, title, data, options=None):
        self.content.append(render_chart(chart_type, title, data, options=options))
        self._types.append("chart")
        if options and "height" in options:
            self._chart_heights.append(options["height"])
        return self

    def render(self):
        return f'<div class="col-span-{self.width}">{"".join(self.content)}</div>'

    def get_component_types(self):
        return self._types

    def get_chart_heights(self):
        return self._chart_heights


class Row:
    def __init__(self, *columns, gap_x=6, gap_y=6):
        self.columns = columns
        self.gap_x = gap_x
        self.gap_y = gap_y

    def render(self):
        return (
            f'<div class="grid grid-cols-12 gap-x-{self.gap_x} gap-y-{self.gap_y} mb-{self.gap_y}">'
            + "".join(col.render() for col in self.columns)
            + "</div>"
        )

    def estimate_height(self):
        height = 0
        for col in self.columns:
            types = col.get_component_types()
            for t in types:
                if t == "card":
                    height = max(height, 180)
                elif t == "table":
                    height = max(height, 320)

            if hasattr(col, "get_chart_heights"):
                for h in col.get_chart_heights():
                    height = max(height, h + 96)
            elif "chart" in types:
                height = max(height, 450)

        return height + 40
