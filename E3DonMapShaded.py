# 
# EISCAT3D field of view plotting routine generated with Google Gemini AI
#
# IV 2026
# 

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.patches import Polygon
import mpl_toolkits.mplot3d.art3d as art3d

def generate_3d_discrete_plates_faded(filename="eiscat3d_plates_faded"):

    # select font size. Larger fonts may require adjustments to site name label positions
    fontsize = 12
    
    # 1. Precise Site Locations (WGS84 Lon, Lat)
    sites = {
        "Skibotn (Tx)": (20.3142, 69.3400),
        "Karesuvanto (Rx)": (22.5236, 68.4803),
        "Kaiseniemi (Rx)": (19.4480, 68.2671)
    }
    
    # 2. Local Coordinate Reference System (Centered at Skibotn)
    center_lon, center_lat = sites["Skibotn (Tx)"]
    proj_km = ccrs.AzimuthalEquidistant(central_longitude=center_lon, central_latitude=center_lat)
    geo_proj = ccrs.Geodetic()
    
    # Transform coordinates to local flat plane in km
    site_coords = {}
    for name, (lon, lat) in sites.items():
        x_m, y_m = proj_km.transform_point(lon, lat, geo_proj)
        site_coords[name] = (x_m / 1000.0, y_m / 1000.0) 
        
    skibotn_x, skibotn_y = site_coords["Skibotn (Tx)"]
    kares_x, kares_y = site_coords["Karesuvanto (Rx)"]
    kaise_x, kaise_y = site_coords["Kaiseniemi (Rx)"]

    # 3. Geomagnetic Pointing Geometry for the Core Tx Beam
    dip_deg = 78.0  
    dec_deg = 11.0  
    theta_math = np.radians(90.0 - (dec_deg + 180.0)) 
    tilt_from_zenith = np.radians(90.0 - dip_deg)
    
    u_x = np.sin(tilt_from_zenith) * np.cos(theta_math)
    u_y = np.sin(tilt_from_zenith) * np.sin(theta_math)
    u_z = np.cos(tilt_from_zenith)

    elevations_deg = 30.0 + np.arange(37) * 1.5  
    elevations_deg = 30.0 + np.arange(20) * 3  
    elevations_rad = np.radians(elevations_deg)
    max_alt = 500.0  

    # 4. Initialize the 3D Engine Layout Canvas
    #fig = plt.figure(figsize=(14, 11), facecolor='#dedede')
    fig = plt.figure(figsize=(14, 11),facecolor='#ffffff')
    ax = fig.add_subplot(111, projection='3d', computed_zorder=False)
    #ax.set_facecolor('#f0f0f0')
    ax.set_facecolor('#ffffff')

    ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 1.0)) # (R, G, B, Alpha)
    ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    
    # Axis limits tightly frame the 300 km plate geometry limits
    xy_limit = 540.0
    ax.set_xlim(-xy_limit, xy_limit)
    ax.set_ylim(-xy_limit, xy_limit)
    ax.set_zlim(0, max_alt)
    ax.set_box_aspect((2 * xy_limit, 2 * xy_limit, max_alt))

    # 5. Compute and Render Smooth Fade-Out Shading at 100, 200, and 300 km Altitudes
    #target_altitudes = [100.0, 200.0, 300.0]
    target_altitudes = [100.0, 300.0]
    min_el_threshold = 30.0
    
    x_space = np.linspace(-xy_limit, xy_limit, 300)
    y_space = np.linspace(-xy_limit, xy_limit, 300)
    X_2d, Y_2d = np.meshgrid(x_space, y_space)

    print("Computing soft fade-out common volume layers...")
    for z in target_altitudes:
        d_skibotn = np.sqrt((X_2d - skibotn_x)**2 + (Y_2d - skibotn_y)**2)
        d_kares = np.sqrt((X_2d - kares_x)**2 + (Y_2d - kares_y)**2)
        d_kaise = np.sqrt((X_2d - kaise_x)**2 + (Y_2d - kaise_y)**2)
        
        el_skibotn = np.degrees(np.arctan2(z, np.where(d_skibotn == 0, 0.001, d_skibotn)))
        el_kares = np.degrees(np.arctan2(z, np.where(d_kares == 0, 0.001, d_kares)))
        el_kaise = np.degrees(np.arctan2(z, np.where(d_kaise == 0, 0.001, d_kaise)))
        
        # Base tracking mask to verify mutual visibility
        valid_mask = (el_skibotn >= min_el_threshold) & (el_kares >= min_el_threshold) & (el_kaise >= min_el_threshold)
        
        if np.any(valid_mask):
            # The average elevation field provides the source data for our gradient mapping
            avg_el = (el_skibotn + el_kares + el_kaise) / 3.0
            
            # Step through several concentric intervals to build up a smooth gradient
            # Lower intervals sit at the low elevation edges and are rendered highly transparent
            shading_levels = np.linspace(min_el_threshold, np.max(avg_el[valid_mask]), 90)
            
            for i in range(len(shading_levels) - 1):
                lvl_min = shading_levels[i]
                
                # Create a mask capturing elements inside this specific core tier
                level_mask = (el_skibotn >= min_el_threshold) & \
                             (el_kares >= min_el_threshold) & \
                             (el_kaise >= min_el_threshold) & \
                             (avg_el >= lvl_min)
                
                if not np.any(level_mask):
                    continue
                
                # Dynamic alpha adjustment: Higher levels get cumulative opacity, 
                # while the outermost level (lowest elevation edges) remains extremely soft
                #base_alpha = 0.035 if i == 0 else 0.025
                base_alpha = 0.012 if i == 0 else 0.012
                
                cs = plt.contour(X_2d, Y_2d, level_mask.astype(float), levels=[0.5], colors='none')
                
                for path in cs.get_paths():
                    verts = path.vertices
                    if len(verts) > 3:
                        if z<200:
                            poly = Polygon(verts, facecolor='#2563eb', edgecolor='none', alpha=base_alpha,zorder=3)
                        else:
                            poly = Polygon(verts, facecolor='#2563eb', edgecolor='none', alpha=base_alpha,zorder=6)
                        ax.add_patch(poly)
                        art3d.pathpatch_2d_to_3d(poly, z=z, zdir="z")
            
            # Draw a single crisp boundary line at the absolute outer edge (30-degree threshold)
            cs_boundary = plt.contour(X_2d, Y_2d, valid_mask.astype(float), levels=[0.5], colors='none')
            for path in cs_boundary.get_paths():
                verts = path.vertices
                if len(verts) > 3:
                    
                    # Label placement near the boundary edge
                    ax.text(verts[0, 0] + 12, verts[0, 1] + 12, z + 2, f"{int(z)} km", 
                            fontsize=fontsize, fontweight='bold', color='#1e40af')
 
    # 6. Safe Coastline Reprojection Layer (Z = 0 floor plate)
    coastline_feature = cfeature.COASTLINE.with_scale('10m')
    for geom in coastline_feature.geometries():
        projected_geom = proj_km.project_geometry(geom, geo_proj)
        sub_geoms = projected_geom.geoms if hasattr(projected_geom, 'geoms') else [projected_geom]
        for sub in sub_geoms:
            coords = sub.exterior.coords if hasattr(sub, 'exterior') else (sub.coords if hasattr(sub, 'coords') else [])
            if len(coords) == 0: continue
            cx, cy = zip(*coords)
            cx, cy = np.array(cx)/1000.0, np.array(cy)/1000.0
            
            mask = (cx > -xy_limit) & (cx < xy_limit) & (cy > -xy_limit) & (cy < xy_limit)
            if np.any(mask):
                ax.plot(cx[mask], cy[mask], zs=0, color='#94a3b8', linewidth=1.2, alpha=0.5, zorder=1)

    # 7. Analytical Ray Tracing Intersection Solver for Individual Beams
    def calculate_intersections_analytic(rx_x, rx_y):
        dx, dy = skibotn_x - rx_x, skibotn_y - rx_y
        A, B, C = u_x**2 + u_y**2, 2 * (u_x * dx + u_y * dy), dx**2 + dy**2
        points = []
        for el in elevations_rad:
            t2 = np.tan(el)**2
            a_c, b_c, c_c = u_z**2 - t2 * A, -t2 * B, -t2 * C
            disc = b_c**2 - 4 * a_c * c_c
            if disc >= 0:
                s1 = (-b_c + np.sqrt(disc)) / (2 * a_c)
                s2 = (-b_c - np.sqrt(disc)) / (2 * a_c)
                
                # Filter for physically forward-pointing rays in the positive altitude space
                valid_roots = [s for s in [s1, s2] if s > 0 and (s * u_z) > 0]
                
                if valid_roots:
                    # CRITICAL FIX: Pick the root that yields the lowest real altitude intersection 
                    # before the beam points completely away back into deep space
                    valid_s = min(valid_roots)
                    pz = valid_s * u_z
                    if pz <= max_alt:
                        points.append((skibotn_x + valid_s * u_x, skibotn_y + valid_s * u_y, pz))
                        continue
            points.append((None, None, None))
        return points

    # 8. Plot the Beams over the Volume (Double-Split at 100km and Intersection Altitudes)
    s_max_draw = max_alt / u_z
    s_steps = np.linspace(0, s_max_draw, 200)
    
    # Split the main Skibotn Tx Column at 100km and 300km boundaries
    tx_alt = s_steps * u_z
    tx_low = tx_alt <= 100.0
    tx_mid = (tx_alt > 100.0) & (tx_alt <= 300.0)
    tx_high = tx_alt > 300.0
    
    ax.plot(skibotn_x + s_steps[tx_low]*u_x, skibotn_y + s_steps[tx_low]*u_y, tx_alt[tx_low], color='red', linewidth=3.5, alpha=0.9, label="Skibotn Tx Column", zorder=2)
    ax.plot(skibotn_x + s_steps[tx_mid]*u_x, skibotn_y + s_steps[tx_mid]*u_y, tx_alt[tx_mid], color='red', linewidth=3.5, alpha=0.9, zorder=4)
    ax.plot(skibotn_x + s_steps[tx_high]*u_x, skibotn_y + s_steps[tx_high]*u_y, tx_alt[tx_high], color='red', linewidth=3.5, alpha=0.9, zorder=7)

    remote_beam_color = '#000000'  
    beam_length = 500.0  

    dx_kaise = skibotn_x - kaise_x
    dy_kaise = skibotn_y - kaise_y
    azimuth_kaise = np.arctan2(dy_kaise, dx_kaise)
    A_k, B_k, C_k = u_x**2 + u_y**2, 2 * (u_x * dx_kaise + u_y * dy_kaise), dx_kaise**2 + dy_kaise**2
    
    for el in elevations_rad:
        # --- PRE-COMPUTE CHANNELS FOR KAISENIEMI ---
        bx_k = beam_length * np.cos(el) * np.cos(azimuth_kaise)
        by_k = beam_length * np.cos(el) * np.sin(azimuth_kaise)
        bz_k = beam_length * np.sin(el)
        
        # --- PRE-COMPUTE CHANNELS FOR KARESUVANTO ---
        # Find the intersection altitude on Tx column first
        t2 = np.tan(el)**2
        a_c, b_c, c_c = u_z**2 - t2 * A_k, -t2 * B_k, -t2 * C_k
        disc = b_c**2 - 4 * a_c * c_c
        
        if disc >= 0:
            s1 = (-b_c + np.sqrt(disc)) / (2 * a_c)
            s2 = (-b_c - np.sqrt(disc)) / (2 * a_c)
            valid_roots = [s for s in [s1, s2] if s > 0 and (s * u_z) > 0]
            if valid_roots:
                valid_s = min(valid_roots)
                pz = valid_s * u_z
                px = skibotn_x + valid_s * u_x
                py = skibotn_y + valid_s * u_y
                
                # Setup Karesuvanto structural vector coordinates
                vx = px - kares_x
                vy = py - kares_y
                vz = pz - 0
                dist_kr = np.sqrt(vx**2 + vy**2 + vz**2)
                bx_kr = (vx / dist_kr) * beam_length
                by_kr = (vy / dist_kr) * beam_length
                bz_kr = (vz / dist_kr) * beam_length

                # --- RENDER KAISENIEMI (3 SEGMENTS) ---
                # Calculate the distance along this specific ray to hit exactly 100km altitude
                s_100_kaise = 100.0 / np.sin(el)
                px_100_k = kaise_x + s_100_kaise * np.cos(el) * np.cos(azimuth_kaise)
                py_100_k = kaise_y + s_100_kaise * np.cos(el) * np.sin(azimuth_kaise)
                
                if 100.0 < pz:
                    # Segment 1: Ground to 100km (Behind lower plate)
                    ax.plot([kaise_x, px_100_k], [kaise_y, py_100_k], [0, 100.0], color=remote_beam_color, linewidth=0.6, alpha=0.8, zorder=2)
                    # Segment 2: 100km to Intersection Point (In-between plates)
                    ax.plot([px_100_k, px], [py_100_k, py], [100.0, pz], color=remote_beam_color, linewidth=0.6, alpha=0.8, zorder=8)
                else:
                    # If intersection is below 100km, skip middle split layer
                    ax.plot([kaise_x, px], [kaise_y, py], [0, pz], color=remote_beam_color, linewidth=0.6, alpha=0.8, zorder=8)
                
                # Segment 3: Intersection Point to Outer Limit (On top of upper plates)
                ax.plot([px, kaise_x + bx_k], [py, kaise_y + by_k], [pz, bz_k], color=remote_beam_color, linewidth=0.6, alpha=0.8, zorder=8)

                # --- RENDER KARESUVANTO (3 SEGMENTS) ---
                # Calculate look direction unit angles for Karesuvanto to find its 100km split coordinates
                s_100_kares = 100.0 / (vz / dist_kr)
                px_100_kr = kares_x + (vx / dist_kr) * s_100_kares
                py_100_kr = kares_y + (vy / dist_kr) * s_100_kares
                
                if 100.0 < pz:
                    # Segment 1: Ground to 100km (Behind lower plate)
                    ax.plot([kares_x, px_100_kr], [kares_y, py_100_kr], [0, 100.0], color=remote_beam_color, linewidth=0.6, alpha=0.8, zorder=2)
                    # Segment 2: 100km to Intersection Point (In-between plates)
                    ax.plot([px_100_kr, px], [py_100_kr, py], [100.0, pz], color=remote_beam_color, linewidth=0.6, alpha=0.8, zorder=8)
                else:
                    # If intersection is below 100km, skip middle split layer
                    ax.plot([kares_x, px], [kares_y, py], [0, pz], color=remote_beam_color, linewidth=0.6, alpha=0.8, zorder=8)
                
                # Segment 3: Intersection Point to Outer Limit (On top of upper plates)
                ax.plot([px, kares_x + bx_kr], [py, kares_y + by_kr], [pz, bz_kr], color=remote_beam_color, linewidth=0.6, alpha=0.8, zorder=8)

                
    # 9. Perspective View Configuration
    ax.view_init(elev=20, azim=-30)  
    ax.set_xlabel("East (km)", fontsize=fontsize)
    ax.set_ylabel("North (km)", fontsize=fontsize)
    ax.set_zlabel("Altitude (km)", fontsize=fontsize)

    
    # 10. Label Core Base Stations
    for name, (x, y) in site_coords.items():
        ax.scatter(x, y, 0, color='yellow', edgecolor='black', s=90, linewidth=1.5, zorder=9)
        if name == "Kaiseniemi (Rx)":
            ax.text(x - 80, y - 300, 2, name, fontsize=fontsize, fontweight='bold', zorder=10)
        else:
            ax.text(x + 20, y + 10, 2, name, fontsize=fontsize, fontweight='bold', zorder=10)
        
    plt.show()
    fig.savefig(filename+'.svg', format='svg', bbox_inches='tight', pad_inches=0.1)
    fig.savefig(filename+'.pdf', format='pdf', bbox_inches='tight', pad_inches=0.1)
    print(f"Edge-faded vector layout successfully saved as '{filename}'.svg and '{filename}'.pdf")

if __name__ == "__main__":
    generate_3d_discrete_plates_faded()
