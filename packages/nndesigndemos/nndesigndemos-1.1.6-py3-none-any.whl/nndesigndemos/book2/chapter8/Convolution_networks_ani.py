import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

from PyQt6 import QtWidgets, QtCore
from nndesigndemos.book2.chapter8.utils import PatternPlot
from nndesigndemos.book2.chapter8.Convolution_networks import Convol


class ConvolAnimation(Convol):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(ConvolAnimation, self).__init__(w_ratio, h_ratio, dpi, res_x_offset=100)
        
        self.animation_speed = 500  # ms between animation frames
        self.is_animating = False
        self.animation = None
        
        # Animation data
        self.current_step = 0
        self.total_steps = 0
        self.animation_frames = []

        # Animation controls
        ani_x = self.x_chapter_usual - 200
        self.make_label(
            "ani_txt",
            # "Animation Part:\n\nUse the toggle to enable\nand disable animation.\nChange animation speed\nwith the slider.\nUse the button to pause\nand resume animation.",
            "Animation Part:\n\nWatch the animation to see\nhow convolution works.",
            (ani_x+10, 330, 150, 200)
        )
        
        self.animation_enabled = False
        # Add animation checkbox
        self.make_checkbox('checkbox_animation', 'Enable Animation', (ani_x, 490, self.w_chapter_slider, 40),
                          self.toggle_animation, self.animation_enabled)

        self.make_label("label_animation", "Animation Speed:", (ani_x + 20, 530, 150, 50))
        self.make_slider("slider_animation", QtCore.Qt.Orientation.Horizontal, (100, 1000), QtWidgets.QSlider.TickPosition.TicksBelow, 100, 500,
                        (ani_x, 560, self.w_chapter_slider, 50), self.change_animation_speed)

        # Add pause/play button
        self.make_button("btn_play_pause", "Pause", 
                         (ani_x+10, 620, self.w_chapter_button, self.h_chapter_button),
                         self.toggle_play_pause)
        self.animation_paused = False
        
        # Animation status label
        self.make_label("label_status", "", (self.x_chapter_usual + 20, 715, 300, 50))
    
    def toggle_animation(self):
        """Toggle whether animation is enabled"""
        # If animation is running and we're disabling it, stop it
        if self.checkbox_animation.checkState().value != 2:
            self.animation_enabled = False
            self.stop_animation()
            self.draw_pattern3() # immediately update the response pattern
        else:
            self.animation_enabled = True
            self.prepare_animation_frames()
    
    def prepare_animation_frames(self):
        """Prepare animation frames for visualizing the convolution process"""
        # If already animating, stop it and update the result
        if self.is_animating:
            self.stop_animation()
            
        # Proceed with animation
        self.is_animating = True
        self.label_status.setText("Animating convolution process...")
        
        self.animation_frames = self.get_response_matrix([])
        
        self.current_step = 0
        self.total_steps = len(self.animation_frames)
        
        self.start_animation()
        
    def start_animation(self):
        """Start the animation sequence"""
        if not self.animation_frames:
            self.is_animating = False
            return
            
        self.animation = QtCore.QTimer()
        self.animation.timeout.connect(self.animate_next_step)
        self.animation.start(self.animation_speed)
        
        # Set animation status
        self.animation_paused = False
        self.btn_play_pause.setText("Pause")
        
    def animate_next_step(self):
        """Process the next animation step"""
        if self.current_step >= self.total_steps:
            # Animation complete
            self.stop_animation()
            return
            
        # Get current frame data
        frame = self.animation_frames[self.current_step]
        
        # Highlight the current area being processed on input pattern
        i, j = frame['input_pos']
        self.pattern1.highlight_area(j, self.size1 - i - self.size2, self.size2, self.canvas)  # Use instance variables
        
        # Update the output pattern for this step
        output_i, output_j = frame['output_pos']
        output_matrix = frame['output_matrix']
        output_matrix[output_i, output_j] = frame['value']
        
        # Flip output matrix for display (to match expected orientation)
        display_output = output_matrix[::-1]
        
        # Update the response pattern display
        self.pattern3.remove_text()
        self.pattern3.remove_patch()
        self.pattern3 = PatternPlot(self.axis3, display_output, self.label_on, True, self.kernel_size)
        self.canvas3.draw()
        
        # Highlight the current output cell in the response pattern
        # Convert output indices to display coordinates (since output is flipped)
        response_y = self.size3 - output_i - 1
        self.pattern3.highlight_area(output_j, response_y, 1, self.canvas3)

        # Update status label with calculation details
        value_str = f"Position: ({j}, {self.size1 - i - self.size2}) → Output: {frame['value']}"
        self.label_status.setText(value_str)
        
        # Move to next step
        self.current_step += 1
        
    def stop_animation(self):
        """Stop the animation sequence"""
        if self.animation:
            self.animation.stop()
            
        # Clear highlights
        self.pattern1.clear_highlight(self.canvas)
        self.pattern3.clear_highlight(self.canvas3)
        
        # Update status
        self.label_status.setText("Animation complete")
        self.is_animating = False
        self.animation_paused = False
        self.btn_play_pause.setText("Pause")

    def change_animation_speed(self):
        """Change the animation speed based on slider value"""
        self.animation_speed = 1100 - self.slider_animation.value()
        if self.animation:
            self.animation.setInterval(self.animation_speed)

    def toggle_play_pause(self):
        """Toggle between pausing and resuming the animation"""
        if not self.is_animating:
            # If not currently animating but we have frames, restart animation
            if self.animation_frames and self.checkbox_animation.checkState().value == 2:
                self.start_animation()
            return
            
        if self.animation_paused:
            # Resume animation
            self.animation_paused = False
            self.btn_play_pause.setText("Pause")
            self.animation.start(self.animation_speed)
            self.label_status.setText("Animation resumed")
        else:
            # Pause animation
            self.animation_paused = True
            self.btn_play_pause.setText("Play")
            if self.animation:
                self.animation.stop()
            self.label_status.setText("Animation paused")
