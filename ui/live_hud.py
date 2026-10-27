"""Full-screen inspired three-column OpenCV dashboard. BGR image in, BGR image out."""
from collections.abc import Mapping
import cv2
import numpy as np

BG=(19,12,5); PANEL=(38,25,12); EDGE=(85,68,44)
WHITE=(250,248,242); MUTED=(188,177,156); CYAN=(244,197,34)
GREEN=(115,225,34); ORANGE=(52,171,255)
W,H=1600,900

def txt(img,s,x,y,size=.55,color=WHITE,th=1,maxw=None):
    s=str(s)
    if maxw:
        while s and cv2.getTextSize(s,cv2.FONT_HERSHEY_SIMPLEX,size,th)[0][0]>maxw:
            s=s[:-2]+'…' if len(s)>3 else ''
    cv2.putText(img,s,(int(x),int(y)),cv2.FONT_HERSHEY_SIMPLEX,size,color,th,cv2.LINE_AA)

def panel(img,x,y,w,h,title=None):
    cv2.rectangle(img,(x,y),(x+w,y+h),PANEL,-1)
    cv2.rectangle(img,(x,y),(x+w,y+h),EDGE,1)
    if title: txt(img,title,x+18,y+32,.61,CYAN,2)

def bar(img,x,y,w,pct,color=GREEN):
    pct=max(0.,min(1.,float(pct)))
    cv2.rectangle(img,(x,y),(x+w,y+12),(67,57,44),-1)
    if pct: cv2.rectangle(img,(x,y),(x+int(w*pct),y+12),color,-1)

def safe_number(value,default=0):
    try:
        number=float(value)
        return number if np.isfinite(number) else default
    except (ValueError,TypeError,OverflowError): return default

def render_dashboard(frame,landmarks,result,*,fps=0.0,side='left',paused=False,workout=None):
    if not isinstance(frame,np.ndarray) or frame.ndim!=3 or frame.shape[2]!=3 or not frame.size:
        raise ValueError('frame must be a nonempty BGR image')
    result=result if isinstance(result,Mapping) else {}
    metrics=result.get('metrics',{}); metrics=metrics if isinstance(metrics,Mapping) else {}
    feedback=result.get('feedback',{}); feedback=feedback if isinstance(feedback,Mapping) else {}
    out=np.full((H,W,3),BG,dtype=np.uint8)
    # Live video is fitted into the central area without distorting its aspect ratio.
    vx,vy,vw,vh=408,95,785,755
    fh,fw=frame.shape[:2]; factor=min(vw/fw,vh/fh)
    nw,nh=max(1,int(fw*factor)),max(1,int(fh*factor))
    video=cv2.resize(frame,(nw,nh),interpolation=cv2.INTER_LINEAR)
    ox,oy=vx+(vw-nw)//2,vy+(vh-nh)//2
    out[oy:oy+nh,ox:ox+nw]=video
    from ar.overlay import SKELETON_CONNECTIONS,_valid_point
    pts={name:_valid_point(pt,fw,fh) for name,pt in (landmarks or {}).items()}
    coords={name:(ox+int(pt[0]*factor),oy+int(pt[1]*factor)) for name,pt in pts.items() if pt is not None}
    for a,b in SKELETON_CONNECTIONS:
        if a in coords and b in coords: cv2.line(out,coords[a],coords[b],WHITE,3,cv2.LINE_AA)
    for point in coords.values(): cv2.circle(out,point,6,GREEN,-1,cv2.LINE_AA)
    # Top application navigation.
    cv2.rectangle(out,(0,0),(W,91),BG,-1)
    txt(out,'AR SPORTS',28,43,.95,WHITE,2)
    txt(out,'COACH',221,43,.95,CYAN,2)
    txt(out,'YOUR PERSONAL AI FITNESS COACH',30,70,.39,MUTED)
    for x,title in [(480,'WORKOUT'),(650,'LIVE TRACKING'),(862,'AI COACHING')]:
        cv2.rectangle(out,(x,18),(x+155,71),PANEL,-1)
        cv2.rectangle(out,(x,18),(x+155,71),EDGE,1)
        txt(out,title,x+13,50,.45,CYAN if x==480 else WHITE)
    txt(out,'M  MUSIC     F  FULL SCREEN',1250,50,.44,GREEN)
    # Left rail.
    panel(out,16,105,374,333,'CUSTOM WORKOUT')
    goals=workout.get('goals') if isinstance(workout,Mapping) else None
    reps_goal=getattr(goals,'repetitions',12)
    minutes=getattr(goals,'minutes',5)
    kcal_goal=getattr(goals,'calorie_target',0)
    for i,(label,value) in enumerate([('EXERCISE','SQUATS'),('REPETITION GOAL',f'{reps_goal} reps'),('DURATION',f'{minutes} min'),('CALORIE TARGET',f'{kcal_goal:g} kcal' if kcal_goal else 'Optional')]):
        y=175+i*60
        txt(out,label,33,y,.45,MUTED)
        txt(out,value,220,y,.53,WHITE,2,maxw=150)
        cv2.line(out,(32,y+16),(375,y+16),EDGE,1)
    txt(out,'ACTIVE WORKOUT',35,417,.61,GREEN,2)
    panel(out,16,454,374,390,'LIVE METRICS')
    reps=max(0,int(safe_number(metrics.get('reps',0))))
    elapsed=max(0,safe_number(workout.get('elapsed',0))) if isinstance(workout,Mapping) else 0
    calories=max(0,safe_number(workout.get('calories',0))) if isinstance(workout,Mapping) else 0
    remaining=max(0,int(minutes*60-elapsed))
    for y,label,value,pct,color in [
        (530,'REPETITIONS',f'{reps} / {reps_goal}',reps/max(reps_goal,1),GREEN),
        (631,'TIME REMAINING',f'{remaining//60:02d}:{remaining%60:02d}',elapsed/max(minutes*60,1),CYAN),
        (732,'EST. CALORIES',f'{calories:.1f} kcal',calories/max(kcal_goal,1) if kcal_goal else 0,ORANGE)]:
        txt(out,label,35,y,.49,MUTED)
        txt(out,value,35,y+42,.94,color,2)
        bar(out,35,y+53,318,pct,color)
    # Camera labels and knee angle.
    cv2.rectangle(out,(vx,vy),(vx+vw,vy+vh),CYAN,2)
    cv2.rectangle(out,(vx+16,vy+16),(vx+230,vy+148),PANEL,-1)
    txt(out,'KNEE ANGLE',vx+33,vy+48,.52,WHITE,2)
    angle=metrics.get('knee_angle')
    angle_label=f'{safe_number(angle):.0f} deg' if angle is not None and np.isfinite(safe_number(angle,float('nan'))) else '--'
    txt(out,angle_label,vx+33,vy+107,1.18,GREEN,3)
    txt(out,f'{side.upper()} LEG  |  {safe_number(fps):.0f} FPS',vx+vw-260,vy+32,.45,WHITE)
    if isinstance(workout,Mapping) and workout.get('completed'):
        cv2.rectangle(out,(vx+175,vy+vh-105),(vx+vw-175,vy+vh-30),PANEL,-1)
        cv2.rectangle(out,(vx+175,vy+vh-105),(vx+vw-175,vy+vh-30),GREEN,3)
        txt(out,'GOAL ACHIEVED!',vx+206,vy+vh-56,.92,GREEN,2)
    # Right rail.
    panel(out,1210,105,374,425,'COACHING FEEDBACK')
    message=str(feedback.get('message','Stand in view'))
    status=str(feedback.get('status','waiting')).lower()
    status_color=GREEN if status in ('good','success') else ORANGE if status in ('warning','error') else CYAN
    cv2.rectangle(out,(1225,161),(1569,271),PANEL,-1)
    cv2.rectangle(out,(1225,161),(1569,271),status_color,2)
    txt(out,'LIVE COACH',1245,193,.52,status_color,2)
    words=message.split(); lines=[]; current=''
    for word in words:
        proposed=(current+' '+word).strip()
        if cv2.getTextSize(proposed,cv2.FONT_HERSHEY_SIMPLEX,.51,1)[0][0]>300 and current:
            lines.append(current);current=word
        else:current=proposed
    if current:lines.append(current)
    for i,line in enumerate(lines[:3]):txt(out,line,1245,224+i*22,.51,WHITE)
    txt(out,'EXERCISE STATE',1231,324,.49,MUTED)
    txt(out,str(metrics.get('state','waiting')).upper(),1231,362,.77,GREEN,2,maxw=320)
    txt(out,'TRACKING  '+side.upper()+' LEG',1231,415,.48,CYAN)
    txt(out,'Stand back to show hip, knee, ankle.',1231,468,.41,MUTED)
    panel(out,1210,548,374,296,'SESSION STATUS')
    txt(out,'POSE TRACKING',1230,603,.55,WHITE)
    txt(out,'LIVE' if coords else 'WAITING FOR POSE',1230,639,.65,GREEN if coords else ORANGE,2)
    txt(out,'WORKOUT PROGRESS',1230,696,.50,MUTED)
    bar(out,1230,718,323,reps/max(reps_goal,1),GREEN)
    txt(out,f'{min(100,int(reps/max(reps_goal,1)*100))}% of rep goal',1230,754,.55,WHITE)
    txt(out,'Calories are illustrative estimates.',1230,815,.42,MUTED)
    # Bottom keyboard shortcuts.
    cv2.rectangle(out,(0,853),(W,899),BG,-1)
    txt(out,'Q QUIT     R RESET     P PAUSE     L SWITCH LEG     M MUSIC     F / ESC FULL SCREEN',31,883,.52,WHITE)
    if paused:
        cv2.rectangle(out,(vx+270,vy+315),(vx+520,vy+405),PANEL,-1)
        txt(out,'PAUSED',vx+313,vy+372,1.0,ORANGE,2)
    return out
