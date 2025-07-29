import marimo

__generated_with = "0.13.15"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    center = lambda text: mo.center(mo.md(text))
    return center, mo


@app.cell
def _(center):
    center("# What is `afterpython`?")
    return


@app.cell
def _(mo):
    mo.Html(f'''
    <p style="font-size: 24px; text-align: center;">
    Why AfterPython?
    - It is a simple and easy-to-use tool for creating websites.
    - It is designed to be used by Python developers.
    - It is open source and free to use.
    </p>
    ''')
    return


@app.cell
def _(center, mo):
    mo.callout(
        center("## *`Every Python project deserves a standalone website, not just a README.md`*"),
        kind="info"
    )
    return


@app.cell
def _(center):
    center("# Why use `afterpython`?")
    return


@app.cell
def _(mo):
    mo.Html(f'''
    <p style="font-size: 24px; text-align: center;  margin-bottom: 2.8rem;">
    Why AfterPython?
    - It is a simple and easy-to-use tool for creating websites.
    - It is designed to be used by Python developers.
    - It is open source and free to use.
    <hr>
    </p>
    ''')
    return


@app.cell
def _(center):
    center(
        r"""
        # Features
        - one
        - two
        - three
        """
    ).style({"margin": "2.8rem"})
    return


@app.cell
def _(center):
    center("""
        # Steps to create a website
        - one
        - two
        - three
    """
    ).style({"margin-bottom": "2.8rem"})
    return


@app.cell
def _(center):
    center("# Examples using `afterpython`:").style({"padding-bottom": "1.2rem"})
    return


@app.cell
def _(mo):
    mo.carousel([
        mo.md("### Example 1"),
        mo.md("### Example 2"),
        # mo.md("![marimo moss ball](https://marimo.app/logotype-wide.svg)"),
        mo.md("### Example 3"),
    ]).style({"margin-bottom": "2.8rem"})
    return


@app.cell
def _(center):
    center("# Community")
    return


@app.cell
def _(mo):
    active_users = mo.stat(
        value="1.2M", 
        label="Active Users", 
        caption="12k from last month", 
        direction="increase"
    )

    revenue = mo.stat(
        value="$4.5M", 
        label="Revenue", 
        caption="8k from last quarter", 
        direction="increase"
    )

    conversion = mo.stat(
        value="3.8", 
        label="Conversion Rate", 
        caption="0.5 from last week", 
        direction="decrease",
    )

    mo.hstack([active_users, revenue, conversion], justify="center", gap="2rem")
    return


@app.cell
def _(center):
    center("# FAQs").style({"margin-top": "2.8rem"})
    return


@app.cell
def _(mo):
    mo.accordion(
        {
            "Question 1": mo.md("Nothing!"),
            "Question 2": mo.md("Nothing!"),
            "Question 3": mo.md(
                "![goat](https://images.unsplash.com/photo-1524024973431-2ad916746881)"
            ),
        }
    )
    return


if __name__ == "__main__":
    app.run()
