from flask import Flask, send_file
import matplotlib.pyplot as plt

app = Flask(__name__)

@app.route('/')
def index():
    # Create the plot
    plt.plot([1, 2, 3], [4, 5, 6])
    plt.title("Sample Graph")

    # Save it as an image
    plot_filename = 'my_plot.png'
    plt.savefig(plot_filename)
    plt.close()  # Close the plot to avoid overwriting

    # Return the image as the HTTP response
    return send_file(plot_filename, mimetype='image/png')

if __name__ == "__main__":
    app.run()