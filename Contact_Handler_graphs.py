#Olivia Creasey
#Bioengineering PhD Candidate; Gartner Lab UCSF
#September 2019
#edited September 2021 for 147_mini_1

"""This module provides functions to automatically create and save
assorted graphs of the data associated with Contact Handler."""

def make_intensities_plot(component_channels_dict):
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt
    #plt.rcParams['animation.ffmpeg_path'] = '/usr/local/bin/ffmpeg'
    import matplotlib.animation as animation

    #Writer = animation.writers['ffmpeg']
    #Writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)
    #Writer = animation.FFMpegWriter(fps=30, codec='libx264')  #or 
    Writer = animation.FFMpegWriter(fps=20, metadata=dict(artist='Me'), bitrate=1800)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    x = []
    y = []
    z = []
    for component, channels in component_channels_dict.items():
        x.append(channels[0][1]) #647
        y.append(channels[3][1]) #405
        z.append(channels[2][1]) #488

    ax.scatter(x, y, z, c='k', marker='o')

    ax.set_title('Surface object mean channel intensities')
    ax.set_xlabel('647')
    ax.set_ylabel('405')
    ax.set_zlabel('488')

    plt.show()

""" def animate(i):
        ax.view_init(30,i)
        plt.draw()

    ani=animation.FuncAnimation(fig, animate, frames = 360, repeat = True)

    ani.save('RelativeMedianChannelIntensities.mov', fps = 20)"""

