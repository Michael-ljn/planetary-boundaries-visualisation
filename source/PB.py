import numpy as np
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
pal = ["#001219","#005f73","#0a9396","#94d2bd","#e9d8a6","#ee9b00","#ca6702","#bb3e03","#ae2012","#9b2226"]
plt.rcParams["axes.prop_cycle"] = plt.cycler('color', pal)
plt.rcParams['lines.linewidth'] = 1.5
font_path = 'source/Harding Text Web Regular Regular.ttf'
font_prop = fm.FontProperties(fname=font_path,size=12, weight='bold')

class PBchart:
    """ Class to create a radar chart with multiple categories and values.  
    """
    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)
        return instance.chart()
    
    def __init__(self, categories, values,upper,lower,legend,figsize=(8, 8),offsetcat=0,scale=None,minscale=None,median_lw=0.8,axis=None):
        self.categories = categories
        self.categories =  self.categories[-2:] +self.categories[:-2]
        self.num_categories = len(categories)
        self.num_values = len(values)
        self.legend=legend
        self.figsize = figsize
        self.mean_vals = values #(minimum of the 3 values)
        self.mean_vals_lw = np.array(values)*median_lw #(minimum of the 3 values)
        self.upper_vals = upper
        self.lower_vals = lower
        self.minscale=minscale  
        self.min_value = np.min(lower)
        self.axis=axis
        
        
        if minscale:
            power_of_ten = np.abs(minscale)
        else:
            power_of_ten = -np.log10(self.min_value)

        
        self.scaling_factor = 10 ** power_of_ten
        self.aSOS_circle_value = np.log10(10 ** power_of_ten)
        self.aSOS_inner_circle_value = np.log10((10 ** power_of_ten)/10)
        
        self.mean_vals=[np.array([np.log10(value*self.scaling_factor) if value > 0 else value for value in listing]) for listing in self.mean_vals]
        self.mean_vals_lw=[np.array([np.log10(value*self.scaling_factor) if value > 0 else value for value in listing]) for listing in self.mean_vals_lw]
        self.lower_vals=[np.array([np.log10(value*self.scaling_factor) if value > 0 else value for value in listing]) for listing in self.lower_vals]
        self.upper_vals=[np.array([np.log10(value*self.scaling_factor) if value > 0 else value for value in listing]) for listing in self.upper_vals]


        if scale:
            self.max_range= scale
            self.max_value = 10**scale
        else:
            self.max_range= np.max(self.upper_vals)
            self.max_value = np.max(upper)
     

        self.full_rotation=2*np.pi
        self.dtheta_categories = self.full_rotation / self.num_categories
        self.dtheta_bar = self.dtheta_categories / self.num_values

        self.angles = np.arange(0, self.full_rotation, self.dtheta_categories)+np.pi/2

        self.label_angles = np.arange(0, self.full_rotation, self.dtheta_categories)+self.dtheta_categories-offsetcat

        self.bar_angles1 = np.arange(0, self.dtheta_categories, self.dtheta_bar)
        self.bar_angles2 = [np.array(self.bar_angles1)+i for i in self.angles[0:-1]]
        self.bar_angles = np.concatenate(self.bar_angles2)

    def create_bar(self,angle, ax, values, color, width, order,hatching=None,alpha=1,edgecolor="black",lw=0.5,linestyle="-"):
        for idx, (angle, value) in enumerate(zip(angle, values)):
            if value < 0:
                value =  np.log10(1000*self.scaling_factor)
                ax.bar(angle+width*(order+1/2), value, width=width, color="lightgrey", edgecolor="none",linewidth=lw,linestyle=linestyle, alpha=0.3,hatch="//")
            else:
                ax.bar(angle+width*(order+1/2), value, width=width, color=color, edgecolor=edgecolor,linewidth=lw,linestyle=linestyle, alpha=alpha,hatch=hatching)
    
    def create_bar_sos(self,angle, ax, values, color, width, order,alpha=0.3,edgecolor="black",linestyle="--"):
        for idx, (angle, value) in enumerate(zip(angle, values)):
            ax.bar(angle+width*(order+1/2), value, width=width, color=color, edgecolor=edgecolor, alpha=alpha,linestyle=linestyle)

    def create_line(self, angle, ax, values, color, width, order, linestyle='-', linewidth=1,reducing_factor=0):
        for idx, (angle, value) in enumerate(zip(angle, values)):
            start_angle = angle + width * (order)
            end_angle = angle + width * (order + 1)
            if value < 0:
                pass
                # value =  np.log10(np.abs(value)*self.scaling_factor)
                # theta = np.linspace(start_angle+reducing_factor, end_angle-reducing_factor, 2) 
                # ax.plot(theta, [value, value], color=color, linestyle="-.", linewidth=linewidth)
            else:
                theta = np.linspace(start_angle+reducing_factor, end_angle-reducing_factor, 2) 
                ax.plot(theta, [value, value], color=color, linestyle=linestyle, linewidth=linewidth)
    
    def create_bar_with_bottom(self, angle, ax, bottom_values, top_values, color, width, order, hatching=None, alpha=1, edgecolor="black", lw=0.5, linestyle="-"):
        for idx, (angle, bottom, top) in enumerate(zip(angle, bottom_values, top_values)):
            # Calculate the height of the bar
            if bottom < 0 and top < 0:
                pass
                # bottom =  np.log10(1)
                # top = np.log10(1)
                # height = top - bottom
                # ax.bar(angle + width * (order + 1 / 2), height, width=width, bottom=bottom,
                # color=color, edgecolor=edgecolor, linewidth=lw, linestyle=linestyle, alpha=alpha, hatch="//")
            else: 
                height = top - bottom
                # Plot the bar with specified bottom and height
                ax.bar(angle + width * (order + 1 / 2), height, width=width, bottom=bottom,
                    color=color, edgecolor=edgecolor, linewidth=lw, linestyle=linestyle, alpha=alpha, hatch=hatching)
    
    def chart(self):
        if self.axis==None:
            fig, ax = plt.subplots(figsize=self.figsize, subplot_kw=dict(polar=True))
        else:
            ax=self.axis

        # powers of 10 within the specified range
        if self.minscale:
            start_exponent = self.minscale
        else:
            start_exponent = int(np.log10(self.min_value))

        end_exponent = int(np.log10(self.max_value))

        scale_points = np.logspace(start_exponent, end_exponent, end_exponent - start_exponent + 1)
        scale_pointsx = [i for i in scale_points if i >= 0.1]
    
        # tick values
        for i in scale_pointsx:
            ticking=np.log10((i)*self.scaling_factor)
            text_angle=np.pi/2.05
            ax.annotate(f'{i}', 
                        xy=(text_angle, ticking), 
                        xytext=(text_angle, ticking), 
                        color='black',
                        fontproperties=font_prop,
                        fontsize=9)
        
        # # tick circles
        for i in scale_points:
            circle = plt.Circle((0, 0), np.log10(i*self.scaling_factor), transform=ax.transData._b, color="k", fill=False, alpha=0.05, linestyle='-', linewidth=1.1)
            ax.add_artist(circle)

        # bar plotting upper values
        al=1
        background_color = "white"
        white_alpha=0
        lw=0.7

        for vals,count in zip(self.upper_vals,np.arange(0,self.num_values,1)): #upper values
            self.create_line(angle=self.angles ,ax=ax, values=vals, color="k", width=self.dtheta_bar, order=count,linestyle='-',linewidth=lw,reducing_factor=0.1)


        for bottom_vals, top_vals, count in zip(self.lower_vals,self.upper_vals, np.arange(0, self.num_values, 1)):
            self.create_bar_with_bottom(angle=self.angles, ax=ax,
                                        bottom_values=bottom_vals, top_values=top_vals,
                                        color=pal[count + 1], width=self.dtheta_bar, order=count,
                                        hatching=None, alpha=0.4, edgecolor="black", lw=0, linestyle="-")
            
        for vals,count in zip(self.mean_vals,np.arange(0,self.num_values,1)): #upper values
            self.create_line(angle=self.angles ,ax=ax, values=vals, color=pal[count + 1], width=self.dtheta_bar, order=count,linestyle='-', linewidth=1.5,reducing_factor=0.1)

        for vals,count in zip(self.lower_vals,np.arange(0,self.num_values,1)): #mean values
            self.create_bar(angle=self.angles ,ax=ax, values=vals, color=pal[count+1], width=self.dtheta_bar, order=count,
                            hatching=None,alpha=1,lw=lw,linestyle="-")
            
        
        # Delimitation of categories
        for idx, angle in enumerate(self.angles): #delimitation of categories

            ax.plot([angle, angle], [0, self.max_range+0.5], color='black', linewidth=1)
        
        # text categories
        ax.annotate('', xy=(np.pi/2, self.max_range+0.7), xytext=(np.pi/2, 0), 
            arrowprops=dict(arrowstyle='->', color='black', linewidth=1.5))

        # aSOS circle
        circle = plt.Circle((0, 0), self.aSOS_circle_value, transform=ax.transData._b,edgecolor="#0d2818",alpha=1,linestyle='--', linewidth=1.5,fill=False)
        ax.add_artist(circle)


        ax.set_xticks(self.label_angles)
        wrapped_labels = [label.replace('  ', '\n') for label in self.categories]
        ax.set_xticklabels(wrapped_labels, fontproperties=font_prop, fontsize=10) 

        ax.grid(False)
        ax.spines['polar'].set_visible(False)
        ax.set_yticklabels([])
        legend_elements = [plt.Line2D([0], [0], color=j, lw=4, label=i) for i, j in zip(self.legend, pal[1:])]
        # ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5,-0.1),prop=font_prop,frameon=False,ncol=3)
        plt.close()
        if self.axis:
            return ax,legend_elements
        else:
            return fig
    