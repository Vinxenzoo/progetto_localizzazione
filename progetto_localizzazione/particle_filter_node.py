import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseWithCovarianceStamped, PoseArray, Pose
import numpy as np
import math

class ParticleFilterNode(Node):
    def __init__(self):
        super().__init__('particle_filter_node')

        self.num_particles = 500
        # Matrice: [X, Y, Theta, Peso]
        self.particles = np.zeros((self.num_particles, 4))
        self.inizializza_particelle()

        self.last_time = None

        self.laser_sub = self.create_subscription(LaserScan, '/scan', self.laser_callback, 10)
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        
        self.pose_pub = self.create_publisher(PoseWithCovarianceStamped, '/amcl_pose', 10)
        self.particles_pub = self.create_publisher(PoseArray, '/particles', 10)

        self.timer = self.create_timer(0.5, self.pubblica_particelle)
        self.get_logger().info("✅ Particle Filter (Fasi 1-4) completato! Pronto per la Mappa.")

    def inizializza_particelle(self):
        self.particles[:, 0] = np.random.uniform(-2.0, 2.0, self.num_particles)
        self.particles[:, 1] = np.random.uniform(-2.0, 2.0, self.num_particles)
        self.particles[:, 2] = np.random.uniform(-math.pi, math.pi, self.num_particles)
        self.particles[:, 3] = 1.0 / self.num_particles

    def pubblica_particelle(self):
        msg = PoseArray()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'odom'
        
        for p in self.particles:
            pose = Pose()
            pose.position.x = float(p[0])
            pose.position.y = float(p[1])
            pose.orientation.z = math.sin(p[2] / 2.0)
            pose.orientation.w = math.cos(p[2] / 2.0)
            msg.poses.append(pose)
            
        self.particles_pub.publish(msg)

    def odom_callback(self, msg):
        """Fase 2: Predizione (Spostamento con incertezza)"""
        current_time = self.get_clock().now().nanoseconds / 1e9
        if self.last_time is None:
            self.last_time = current_time
            return
        
        dt = current_time - self.last_time
        self.last_time = current_time

        v = msg.twist.twist.linear.x
        w = msg.twist.twist.angular.z

        if abs(v) < 0.001 and abs(w) < 0.001:
            return

        noise_v = np.random.normal(0.0, 0.1, self.num_particles)
        noise_w = np.random.normal(0.0, 0.05, self.num_particles)

        v_noisy = v + noise_v
        w_noisy = w + noise_w

        self.particles[:, 2] += w_noisy * dt
        self.particles[:, 2] = np.arctan2(np.sin(self.particles[:, 2]), np.cos(self.particles[:, 2]))
        self.particles[:, 0] += v_noisy * np.cos(self.particles[:, 2]) * dt
        self.particles[:, 1] += v_noisy * np.sin(self.particles[:, 2]) * dt

    def laser_callback(self, msg):
        """Fase 3 e 4: Aggiornamento pesi e Resampling"""
        # 1. Leggiamo il laser
        ranges = np.array(msg.ranges)
        valid_ranges = ranges[(ranges > msg.range_min) & (ranges < msg.range_max)]
        
        if len(valid_ranges) == 0:
            return

        # FASE 3: AGGIORNAMENTO PESI
        # (Qui, in futuro, compareremo valid_ranges con la Mappa di Gazebo).
        # Per ora diamo pesi fittizi per preparare la struttura matematica.
        pseudo_prob = np.random.uniform(0.5, 1.5, self.num_particles)
        self.particles[:, 3] *= pseudo_prob

        # Normalizzazione: facciamo in modo che la somma di tutti i pesi faccia 1
        somma_pesi = np.sum(self.particles[:, 3])
        if somma_pesi > 0:
            self.particles[:, 3] /= somma_pesi
        else:
            self.particles[:, 3] = 1.0 / self.num_particles # Reset se si perde

        # FASE 4: RESAMPLING (Selezione Naturale)
        # Estraiamo 500 nuove particelle "pescando" da quelle vecchie.
        # Chi ha un peso maggiore ha più probabilità di essere ri-pescato (e clonato).
        indici_estratti = np.random.choice(
            self.num_particles, 
            self.num_particles, 
            p=self.particles[:, 3], # Probabilità dettata dal peso
            replace=True
        )
        
        # Sovrascriviamo la vecchia generazione con quella nuova e forte!
        self.particles = self.particles[indici_estratti]
        
        # Resettiamo i pesi uniformi per il prossimo ciclo
        self.particles[:, 3] = 1.0 / self.num_particles


def main(args=None):
    rclpy.init(args=args)
    node = ParticleFilterNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()