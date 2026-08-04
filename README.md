# 🤖 Filtro a Particelle (Particle Filter) con ROS 2

Questo pacchetto contiene un Filtro a Particelle personalizzato scritto in Python per ROS 2 (Humble). 
Permette a un robot (TurtleBot3) di localizzarsi all'interno di una mappa nota sfruttando i dati del LaserScan (LiDAR) e l'Odometria.

## 📌 Requisiti
Per far funzionare questo progetto hai bisogno di:
- ROS 2 Humble
- Gazebo (Simulatore 3D)
- Pacchetto nav2_map_server
- Pacchetto turtlebot3_gazebo

## 🚀 Come installare e compilare

1. Clona questa repository dentro la cartella `src` del tuo workspace ROS 2:
   ```bash
   cd ~/ros2_ws/src
   git clone 