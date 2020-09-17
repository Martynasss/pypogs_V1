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
    sys.add_mount(model='Celestron', identity='COM5')
    # sys.update_databases()
    sys.alignment.set_location_lat_lon(lat=52.2157, lon=4.4316, height=45) #ESTEC football field (0m MSL)
    # sys.alignment.set_alignment_enu()
    #
    # tle = ['1 44243C 19029J   20219.38919804 -.00382933  00000-0 -12914-2 0  2198', '2 44243  52.9983 222.2763 0001426  50.9336  62.7758 15.89652207    19'] # STARLINK-29 start time 2020-08-09 20:45:38.000 end time 2020-08-09 20:48:29.000
    # tle = ['1 44259C 19029AA  20222.50750898  .00056373  00000-0  17432-3 0  2228', '2 44259  52.9997 207.2825 0002366  79.7279 157.6069 15.90914653    19'] # STARLINK - 52 start time 2020-08-09 19:30:23.000 end time 2020-08-09 19:35:31.000
    # tle = ['1 25994U 99068A   20222.18332003  .00000078  00000-0  27294-4 0  9992', '2 25994  98.2104 295.7300 0001220 103.0784 257.0568 14.57113309 97990'] # TERRA start time 2020-08-09 20:04:29.000 end time 2020-08-09 20:12:18.000
    # tle = ['1 14699U 84013A   20222.46301725 -.00000145  00000-0 -12074-4 0  9991', '2 14699  82.5255 296.3384 0014619  93.9101 266.3798 15.05613386985996'] # COSMOS 1536  start time 2020-08-09 21:30:13.000 end time 2020-08-09 21:34:26.000
    # tle = ['1 31792U 07029A   20222.26089960 -.00000335  00000-0 -15567-3 0  9998', '2 31792  70.9071 162.0681 0010287 340.7289  19.3441 14.12304654676329'] # COSMOS 2428  start time 2020-08-09 22:47:59.000 end time 2020-08-09 22:52:17.000
    # tle = ['1 39679U 14021B   20222.38524028 -.00000094  00000-0  14045-4 0  9994', '2 39679  51.6139 221.7677 0172212 129.1079 232.5347 15.06456405347328'] # SL-4 R/B  start time 2020-08-09 21:30:13.000 end time 2020-08-09 21:34:26.000
    # tle = ['1 44273U 19029AQ  20222.22199603  .00042216  00000-0  46493-3 0  9995', '2 44273  52.9941 204.5476 0002029 263.4621  96.6161 15.62726985 68832'] # STARLINK-60  start time 2020-08-09 19:58:36.000 end time 2020-08-09 20:04:45.000
    # tle = ['1 40354U 14084B   20221.87880100  .00000674  00000-0  17667-4 0  9990', '2 40354  74.7374 279.6327 0036101  81.5345 278.9956 15.40293991316204'] # SL-27 R/B start time 2020-08-09 21:15:58.000 end time 2020-08-09 21:19:26.000
    # tle = ['1 26474U 00047B   20222.47250601  .00000036  00000-0  14094-4 0  9998', '2 26474  67.9938 289.7519 0052879 143.3725 217.1052 14.95975560 87255']  # TITAN 4B R/B start time 2020-08-09 21:49:42.000 end time 2020-08-09 21:52:31.000
    #
    # sys.target.set_target_from_tle(tle)
    # sys.target.set_target_from_ra_dec(30.530194, 89.26417) #Polaris mano
    sys.target.set_target_from_ra_dec(37.95456067, 89.26410897)  # Polaris      Manually adds target
    # sys.target.set_target_from_ra_dec(285.3686, -22.47972) # Jupiter
    # sys.target.set_target_from_ra_dec(285.935, -21.0230) # Saturn


    # # COARSE/STAR
    sys.coarse_camera.exposure_time_auto = False
    sys.coarse_track_thread.spot_tracker.image_th = 10000

    sys.coarse_camera.exposure_time = 450 #450
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
    sys.fine_camera.exposure_time =150
    sys.fine_camera.gain = 0
    sys.fine_camera.frame_rate = 30
    sys.fine_camera.binning = 2
    sys.fine_camera.plate_scale = .30
    sys.fine_camera.flip_x = False #def True Martyno konfiguracijoje, kai veidrodelis ziuri taip tai turi buti sukeista x asys kad sutaptu su coarse
    sys.fine_camera.flip_y = False
    sys.fine_track_thread.spot_tracker.max_search_radius = 100
    sys.fine_track_thread.spot_tracker.min_search_radius = 10
    sys.fine_track_thread.spot_tracker.crop = (256,256)
    sys.fine_track_thread.spot_tracker.spot_min_sum = 500
    sys.fine_track_thread.spot_tracker.image_th = 50 #50 gustavo buvo
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

