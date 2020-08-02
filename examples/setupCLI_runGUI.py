"""
Example of how to set up the telescope with the CLI before starting GUI.
"""
import sys
sys.path.append('..')

import pypogs
from pathlib import Path

sys = pypogs.System()


try:
    # LOAD
    sys.add_coarse_camera(model='ptgrey', identity='18285284')
    sys.add_star_camera_from_coarse()
    sys.add_fine_camera(model='ptgrey', identity='18285254')
    sys.add_mirror(model='FSM', identity='COM3')
    sys.add_mount(model='Celestron', identity='COM11')
    # sys.update_databases()
    sys.alignment.set_location_lat_lon(lat=52.2154, lon=4.4193, height=3) #ESTEC football field (0m MSL)
    sys.alignment.set_alignment_enu()
    #
    # tle = ['1 25544U 98067A   20210.31705315  .00000912  00000-0  24280-4 0  9992', '2 25544  51.6417 144.8926 0000854 139.1646 324.8066 15.49511599238390'] # iss
    # tle = ['1 00877U 64053B   20212.40782882 -.00000099  00000-0  45963-5 0  9997', '2 00877  65.0764 203.4560 0061665   8.4146 351.7971 14.59395470967753'] # SL-3 R/B
    tle = ['1 16719U 86034A   20212.37231825  .00000578  00000-0  28680-4 0  9991', '2 16719  82.5540 315.4375 0010506 300.4902 120.6704 15.15708970867934']  # COSMOS 1743
    #
    # sys.target.set_target_from_tle(tle)
    # sys.target.set_target_from_ra_dec(37.95456067, 89.26410897)  # Polaris             Manually adds target
    # sys.target.set_target_from_ra_dec(160, 40)


    # # COARSE/STAR
    sys.coarse_camera.exposure_time_auto = False
    sys.coarse_track_thread.spot_tracker.image_th = 10000

    sys.coarse_camera.exposure_time = 0.1 #450
    sys.coarse_camera.gain = 0
    sys.coarse_camera.frame_rate = 5
    sys.coarse_camera.binning = 2 # gal galima nedaryti bining? palikti 1 px tai tada plate scale butu vietoj 40.6 20.3, bet FOV 1.44deg realiai tada sistema nebegaudo tolimesnio tasko
                                  # kai bining 2 tai aptinka apie 4000 arsec coarse camera kai 1 tai 2100 arcsec
    sys.coarse_camera.plate_scale = 20.3 #Therefore that needs to be taken into account in the plate scale (which is defined as the physical pixel size)
    sys.coarse_track_thread.goal_x_y = [0, 0]
    sys.coarse_track_thread.spot_tracker.max_search_radius =500
    sys.coarse_track_thread.spot_tracker.min_search_radius = 200
    sys.coarse_track_thread.spot_tracker.crop = (256,256)
    sys.coarse_track_thread.spot_tracker.spot_min_sum = 500
    sys.coarse_track_thread.spot_tracker.bg_subtract_mode = 'local_median'
    sys.coarse_track_thread.spot_tracker.sigma_mode = 'local_median_abs'
    sys.coarse_track_thread.spot_tracker.fails_to_drop = 10
    sys.coarse_track_thread.spot_tracker.smoothing_parameter = 8 #It roughly corresponds to the number of samples to average
    sys.coarse_track_thread.spot_tracker.rmse_smoothing_parameter = 8
    sys.coarse_track_thread.feedforward_threshold = 10
    sys.coarse_track_thread.img_save_frequency = 0.5
    sys.coarse_track_thread.image_folder = Path(r'C:\Users\Martynas Milaseviciu\ESA\pypogs_V1\examples\tracking_images')

    # # FINE
    sys.fine_camera.exposure_time = 0.1
    sys.fine_camera.gain = 0
    sys.fine_camera.frame_rate =50
    sys.fine_camera.binning = 2
    sys.fine_camera.plate_scale = .30
    sys.fine_camera.flip_x = False #def True Martyno konfiguracijoje, kai veidrodelis ziuri taip tai turi buti sukeista x asys kad sutaptu su coarse
    sys.fine_track_thread.spot_tracker.max_search_radius = 10
    sys.fine_track_thread.spot_tracker.min_search_radius = 5
    sys.fine_track_thread.spot_tracker.crop = (256,256)
    sys.fine_track_thread.spot_tracker.spot_min_sum = 500
    sys.fine_track_thread.spot_tracker.image_th = 8000 #50 gustavo buvo
    sys.fine_track_thread.spot_tracker.bg_subtract_mode = 'global_median'
    sys.fine_track_thread.spot_tracker.fails_to_drop = 20
    sys.fine_track_thread.spot_tracker.smoothing_parameter = 20
    sys.fine_track_thread.spot_tracker.rmse_smoothing_parameter = 20
    sys.fine_track_thread.spot_tracker.spot_max_axis_ratio = None
    sys.fine_track_thread.feedforward_threshold = 5
    sys.fine_track_thread.img_save_frequency = 0.5
    sys.fine_track_thread.image_folder = Path(r'C:\Users\Martynas Milaseviciu\ESA\pypogs_V1\examples\tracking_images')

    # FEEDBACK
    sys.control_loop_thread.integral_max_add = 30
    sys.control_loop_thread.integral_max_subtract = 30
    sys.control_loop_thread.integral_min_rate = 5
    sys.control_loop_thread.OL_P = 1
    sys.control_loop_thread.OL_I = 10
    sys.control_loop_thread.OL_speed_limit = 4*3600
    sys.control_loop_thread.CCL_P = 1
    sys.control_loop_thread.CCL_I = 5
    sys.control_loop_thread.CCL_speed_limit = 360
    sys.control_loop_thread.CCL_transition_th = 100
    sys.control_loop_thread.FCL_P = 2
    sys.control_loop_thread.FCL_I = 5
    sys.control_loop_thread.FCL_speed_limit = 180
    sys.control_loop_thread.FCL_transition_th = 50
    sys.control_loop_thread.CTFSP_spacing = 100
    sys.control_loop_thread.CTFSP_speed = 50
    sys.control_loop_thread.CTFSP_max_radius = 500
    sys.control_loop_thread.CTFSP_transition_th = 20
    sys.control_loop_thread.CTFSP_auto_update_CCL_goal = True
    sys.control_loop_thread.CTFSP_auto_update_CCL_goal_th = 10
    sys.control_loop_thread.CTFSP_disable_after_goal_update = True

    pypogs.GUI(sys, 500)
except Exception:
    raise
finally:
    gc_loop_stop = True
    sys.deinitialize()

