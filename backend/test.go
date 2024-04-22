package main

import (
	"fmt"
	"math"
)

// Representa un punto en el espacio 3D
type Point struct {
	X, Y, Z float64
}

// Representa un rayo (origen y dirección)
type Ray struct {
	Origin    Point
	Direction Point
}

// Función para lanzar rayos y detectar intersecciones con esferas
func RayLaunching(rays []Ray, spheres []Sphere) []Intersection {
	intersections := make([]Intersection, 0)
	for _, ray := range rays {
		for _, sphere := range spheres {
			if intersect := ray.Intersects(sphere); intersect != nil {
				intersections = append(intersections, *intersect)
			}
		}
	}
	return intersections
}

// Representa una esfera (centro y radio)
type Sphere struct {
	Center Point
	Radius float64
}

// Función para detectar intersección entre un rayo y una esfera
func (ray Ray) Intersects(sphere Sphere) *Intersection {
	a := ray.Direction.X*ray.Direction.X + ray.Direction.Y*ray.Direction.Y + ray.Direction.Z*ray.Direction.Z
	b := 2 * (ray.Direction.X*(ray.Origin.X-sphere.Center.X) + ray.Direction.Y*(ray.Origin.Y-sphere.Center.Y) + ray.Direction.Z*(ray.Origin.Z-sphere.Center.Z))
	c := (ray.Origin.X-sphere.Center.X)*(ray.Origin.X-sphere.Center.X) + (ray.Origin.Y-sphere.Center.Y)*(ray.Origin.Y-sphere.Center.Y) + (ray.Origin.Z-sphere.Center.Z)*(ray.Origin.Z-sphere.Center.Z) - sphere.Radius*sphere.Radius
	det := b*b - 4*a*c
	if det < 0 {
		return nil
	}
	t := (-b - math.Sqrt(det)) / (2 * a)
	if t < 0 {
		return nil
	}
	return &Intersection{ray.Origin.Add(ray.Direction.Scale(t)), sphere}
}

// Representa una intersección (punto y esfera)
type Intersection struct {
	Point  Point
	Sphere Sphere
}

// Función para sumar un vector a un punto
func (p Point) Add(v Point) Point {
	return Point{p.X + v.X, p.Y + v.Y, p.Z + v.Z}
}

// Función para escalar un vector
func (v Point) Scale(t float64) Point {
	return Point{v.X * t, v.Y * t, v.Z * t}
}

func main() {
	// Crear rayos y esferas de prueba
	rays := []Ray{
		{Origin: Point{0, 0, 0}, Direction: Point{1, 0, 0}},
		{Origin: Point{0, 0, 0}, Direction: Point{0, 1, 0}},
	}
	spheres := []Sphere{
		{Center: Point{1, 0, 0}, Radius: 1},
		{Center: Point{0, 1, 0}, Radius: 1},
	}

	// Lanzar rayos y detectar intersecciones
	intersections := RayLaunching(rays, spheres)

	// Imprimir resultados
	for _, intersection := range intersections {
		fmt.Printf("Intersección en (%f, %f, %f) con esfera de centro (%f, %f, %f) y radio %f\n",
			intersection.Point.X, intersection.Point.Y, intersection.Point.Z,
			intersection.Sphere.Center.X, intersection.Sphere.Center.Y, intersection.Sphere.Center.Z,
			intersection.Sphere.Radius)
	}
}
