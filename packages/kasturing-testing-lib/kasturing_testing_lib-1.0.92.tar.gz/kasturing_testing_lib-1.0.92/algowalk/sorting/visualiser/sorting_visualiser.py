import plotly.graph_objects as go
from algowalk.utils.visualizer.step_visualizer import StepVisualizer


# Sorting visualizer using Plotly
class PlotlyStepVisualizer(StepVisualizer):

    def visualize(self, steps):
        total = len(steps[0]) if steps else 0

        fig = go.Figure(
            layout=go.Layout(
                title="Sorting Algorithm - Dry run Visualization",
                xaxis=dict(title="Index", range=[-1, total]),
                yaxis=dict(title="Value", range=[0, max(max(step) for step in steps) + 5]),
                updatemenus=[
                    dict(
                        type="buttons",
                        showactive=False,
                        buttons=[
                            dict(
                                label="▶ Play",
                                method="animate",
                                args=[None, {
                                    "frame": {"duration": 1000, "redraw": True},
                                    "fromcurrent": True,
                                    "transition": {"duration": 500, "easing": "linear"}
                                }]
                            ),
                            dict(
                                label="⏸ Pause",
                                method="animate",
                                args=[[None], {
                                    "mode": "immediate",
                                    "frame": {"duration": 0, "redraw": False},
                                    "transition": {"duration": 0}
                                }]
                            )
                        ]
                    )
                ]
            )
        )

        # Initial frame
        fig.add_trace(go.Bar(
            x=list(range(total)),
            y=steps[0],
            marker_color=["gray"] * total,
            hoverinfo="x+y"
        ))

        # Create animation frames
        frames = []
        for i, step in enumerate(steps):
            colors = ["gray"] * total
            if i < len(steps) - 1:
                for j in range(total):
                    if steps[i][j] != steps[i + 1][j]:
                        colors[j] = "yellow"
            else:
                colors = ["green"] * total

            frames.append(go.Frame(
                data=[go.Bar(
                    x=list(range(total)),
                    y=step,
                    marker_color=colors
                )],
                name=f"frame{i}"
            ))

        fig.frames = frames
        fig.show()
