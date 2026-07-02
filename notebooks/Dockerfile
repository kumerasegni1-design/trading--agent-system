FROM jupyter/base-notebook:latest

WORKDIR /workspace

# Install Python dependencies
RUN pip install --no-cache-dir \
    pandas \
    numpy \
    scikit-learn \
    xgboost \
    lightgbm \
    backtrader \
    yfinance \
    ta-lib \
    matplotlib \
    seaborn \
    plotly

# Expose Jupyter
EXPOSE 8888

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--no-browser"]
