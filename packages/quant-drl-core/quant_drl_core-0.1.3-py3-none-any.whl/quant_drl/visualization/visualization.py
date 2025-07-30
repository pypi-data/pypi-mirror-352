import plotly.colors as pc
import plotly.figure_factory as ff
import plotly.graph_objects as go

COLOR_PALETTE = pc.qualitative.Set1


def plot_stock_data(stock_data_df, start_date, end_date, company_name, feature="Close"):
    """
    @param stock_data_df: pandas.DataFrame concatenando los activos
    @param start_date: fecha de inicio para filtrar los datos
    @param end_date: fecha de fin para filtrar los datos
    @param company_name: nombre de la empresa
    @param feature: feature a plotear
    """

    filtered_data = stock_data_df[
        (stock_data_df["Stock"] == company_name)
        & (stock_data_df.index >= start_date)
        & (stock_data_df.index <= end_date)
    ]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=filtered_data.index,
            y=filtered_data[feature],
            mode="lines",
            name=company_name,
        )
    )

    fig.update_layout(
        title=f"{company_name} stock data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
        xaxis_title="Date",
        yaxis_title=feature,
        template="seaborn",
    )

    fig.show()


def plot_multiple_stock_data(
    stock_data_df,
    start_date,
    end_date,
    company_names,
    feature="Close",
    title=None,
    colors=None,
    xlabel="Date",
    ylabel="Value",
):
    """
    @param stock_data_df: pandas.DataFrame concatenando los activos
    @param start_date: fecha de inicio para filtrar los datos
    @param end_date: fecha de fin para filtrar los datos
    @param company_names: lista de nombres de las empresas
    @param feature: feature a plotear
    @param colors: colores opcionales para cada empresa
    @param title: título del gráfico
    """

    filtered_data = stock_data_df[
        (stock_data_df["Stock"].isin(company_names))
        & (stock_data_df.index >= start_date)
        & (stock_data_df.index <= end_date)
    ]

    fig = go.Figure()

    num_companies = len(company_names)
    colors = [COLOR_PALETTE[i % len(COLOR_PALETTE)] for i in range(num_companies)]

    for i, company_name in enumerate(company_names):
        company_data = filtered_data[filtered_data["Stock"] == company_name]
        fig.add_trace(
            go.Scatter(
                x=company_data.index,
                y=company_data[feature],
                mode="lines",
                name=company_name,
                line=dict(color=colors[i]),
            )
        )

    if not title:
        title = f"{feature} stock data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} "

    if not xlabel:
        xlabel = "Date"

    if not ylabel:
        ylabel = feature

    fig.update_layout(
        title=title, xaxis_title=xlabel, yaxis_title=ylabel, template="seaborn"
    )

    fig.show()


def plot_distribution_from_df(
    stock_data_df,
    comp_abv,
    start_date,
    end_date,
    feature="Close",
    title="Distribution of Returns",
    ylabel="Frequency",
    xlabel="Returns",
    bin_size=0.001,
):
    """
    Plots the distribution of the returns for a single company using Plotly.

    Parameters:
    stock_data_df (pandas.DataFrame): The stock data.
    comp_abv (list): List of company abbreviations.
    feature (str): The feature to plot.
    title (str): Title of the plot.
    """

    filtered_data = stock_data_df[
        (stock_data_df["Stock"].isin(comp_abv))
        & (stock_data_df.index >= start_date)
        & (stock_data_df.index <= end_date)
    ]

    hist_data = []
    group_labels = []

    num_companies = len(comp_abv)
    colors = [COLOR_PALETTE[i % len(COLOR_PALETTE)] for i in range(num_companies)]

    for company in comp_abv:
        hist_data.append(
            filtered_data[filtered_data["Stock"] == company][feature].dropna()
        )
        group_labels.append(company)

    fig = ff.create_distplot(
        hist_data,
        group_labels,
        show_hist=True,
        show_rug=False,
        show_curve=True,
        colors=colors,
        bin_size=bin_size,
    )

    if not title:
        title = "Distribution of Returns"

    if not ylabel:
        ylabel = "Frequency"

    if not xlabel:
        xlabel = "Returns"

    fig.update_layout(
        title=title,
        xaxis_title=xlabel,
        yaxis_title=ylabel,
        template="seaborn",
    )

    fig.show()
    return hist_data


def plot_multiindex_stock_data(
    stock_data_df,
    start_date,
    end_date,
    company_names,
    feature="Close",
    colors=None,
    title=None,
    ylabel=None,
    xlabel=None,
):
    """
    @param stock_data_df: pandas.DataFrame con MultiIndex en columnas
    @param start_date: fecha de inicio para filtrar los datos
    @param end_date: fecha de fin para filtrar los datos
    @param company_names: lista de nombres de las empresas
    @param feature: característica a plotear (ej. "Close")
    @param colors: colores opcionales para cada empresa
    @param title: título del gráfico
    """

    # Filtrar por fechas
    filtered_data = stock_data_df.loc[start_date:end_date, :]

    # Filtrar solo las columnas que corresponden a las empresas seleccionadas
    filtered_data = filtered_data.loc[
        :, [(feature, company) for company in company_names]
    ]

    # Generar colores aleatorios si no se especifican
    num_companies = len(company_names)
    colors = [COLOR_PALETTE[i % len(COLOR_PALETTE)] for i in range(num_companies)]

    fig = go.Figure()
    for i, company_name in enumerate(company_names):
        fig.add_trace(
            go.Scatter(
                x=filtered_data.index,
                y=filtered_data[(feature, company_name)],
                mode="lines",
                name=company_name,
                line=dict(color=colors[i]),
            )
        )

    # Configurar título
    if not title:
        title = f"{feature} stock data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

    if not ylabel:
        ylabel = feature

    if not xlabel:
        xlabel = "Date"

    fig.update_layout(
        title=title,
        xaxis_title=xlabel,
        yaxis_title=ylabel,
        template="seaborn",
    )

    fig.show()


def plot_multiple_numpy_data(
    data,
    company_names,
    start_index=0,
    end_index=None,
    title="Numpy Data",
    colors=None,
    xlabel="Index",
    ylabel="Value",
):
    """
    Plots multiple time series data from a numpy array using Plotly.

    @param data: numpy array containing the data
    @param start_index: start index for slicing the data
    @param end_index: end index for slicing the data
    @param stock_names: list of stocks to plot
    @param title: title of the plot
    @param colors: list of colors for the plots
    """

    if end_index is None:
        end_index = data.shape[0]

    sliced_data = data[start_index:end_index, :]

    fig = go.Figure()

    num_companies = len(company_names)
    colors = [COLOR_PALETTE[i % len(COLOR_PALETTE)] for i in range(num_companies)]

    for i, stock_name in enumerate(company_names):
        fig.add_trace(
            go.Scatter(
                y=sliced_data[:, i],
                mode="lines",
                name=f"Stock {stock_name}",
                line=dict(color=colors[i]),
            )
        )

    if not title:
        title = f"Stock data from index {start_index} to {end_index}"

    if not xlabel:
        xlabel = "Index"

    if not ylabel:
        ylabel = "Value"

    fig.update_layout(
        title=f"{title} from index {start_index} to {end_index}",
        xaxis_title=xlabel,
        yaxis_title=ylabel,
        template="seaborn",
    )

    fig.show()


def plot_distribution_from_np(
    returns_np_close, comp_abv, title="Distribution of Returns", colors=None
):
    """
    Plots the distribution of the returns for each company on a single plot with transparency using Plotly.

    Parameters:
    returns_np_close (numpy.ndarray): The returns data.
    comp_abv (list): List of company abbreviations.
    title (str): Title of the plot.
    """

    hist_data = [returns_np_close[:, i] for i in range(len(comp_abv))]

    fig = ff.create_distplot(hist_data, comp_abv, show_hist=True, show_rug=False)
    fig.update_layout(
        title=title,
        xaxis_title="Returns",
        yaxis_title="Frequency",
        template="seaborn",
    )

    fig.show()
