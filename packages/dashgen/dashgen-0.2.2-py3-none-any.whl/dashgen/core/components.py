from dashgen.core.utils import format_currency
from dashgen.charts.chartjs import generate_chartjs_block

def render_card(title, value, target, style=None, currency="R$"):
    style = style or {}

    perc = int((value / target) * 100) if target else 0
    title_color = style.get("title_color", "text-primary")
    title_size = style.get("title_size", "text-lg")
    text_size = style.get("text_size", "text-sm")
    bar_color = style.get("bar_color", "bg-[color:var(--primary)]")
    card_class = style.get("card_class", "bg-white rounded-lg shadow p-4")

    return f'''
    <div class="{card_class}">
        <h3 class="{title_size} font-semibold mb-2 {title_color}">{title}</h3>
        <p class="{text_size} mb-2">
            <strong>{format_currency(value, currency)}</strong> / {format_currency(target, currency)} ({perc}%)
        </p>
        <div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
            <div class="h-full {bar_color}" style="width:{min(100, perc)}%"></div>
        </div>
    </div>
    '''
def render_table(title, data, headers, progress_columns=None, progress_config=None):
    progress_columns = progress_columns or []
    progress_config = progress_config or {
        "below": {"bar_color": "bg-red-400", "text_color": "text-white"},
        "met": {"bar_color": "bg-yellow-400", "text_color": "text-black"},
        "above": {"bar_color": "bg-green-500", "text_color": "text-white"},
    }

    rows = ""
    for row in data:
        row_html = ""
        for h in headers:
            valor = str(row.get(h, ""))

            if h in progress_columns and valor.replace("%", "").replace(",", ".").replace(".", "").isdigit():
                try:
                    perc = float(valor.replace("%", "").replace(",", "."))
                except Exception:
                    perc = 0

                faixa = (
                    "below" if perc < 100 else
                    "met" if perc == 100 else
                    "above"
                )

                bar_color = progress_config[faixa]["bar_color"]
                text_color = progress_config[faixa]["text_color"]

                row_html += f"""
                <td class='px-3 py-2 border-b border-gray-100 text-sm align-middle'>
                    <div class="relative w-full bg-gray-100 rounded h-4 overflow-hidden">
                        <div class="absolute left-0 top-0 h-full {bar_color}" style="width:{min(perc, 100)}%"></div>
                        <div class="relative text-center z-10 text-xs leading-4 {text_color}">{valor}</div>
                    </div>
                </td>
                """
            else:
                row_html += f"<td class='px-3 py-2 border-b border-gray-100 text-sm'>{valor}</td>"
        rows += f"<tr>{row_html}</tr>"

    header_html = "".join([
        f"<th class='text-left text-[color:var(--primary)] font-semibold text-sm px-3 py-2 bg-gray-100'>{h}</th>"
        for h in headers
    ])

    return f'''
    <div class="bg-white rounded-lg shadow p-4">
        <h3 class="text-lg font-semibold mb-3">{title}</h3>
        <div class="overflow-x-auto">
            <table class="w-full border-collapse">
                <thead><tr>{header_html}</tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    </div>
    '''



def render_chart(chart_type, title, data, options=None):
    return generate_chartjs_block(title, data, chart_type=chart_type, options=options)
