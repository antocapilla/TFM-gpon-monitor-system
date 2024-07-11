import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

const ContourMap = ({ heatmapData, geoJsonData, onts, width, height, buildingImageUrl }) => {
  const svgRef = useRef(null);

  useEffect(() => {
    if (!heatmapData || !geoJsonData || !onts) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const margin = { top: 40, right: 100, bottom: 20, left: 20 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const g = svg.append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Add background image
    svg.append("image")
      .attr("xlink:href", buildingImageUrl)
      .attr("x", margin.left)
      .attr("y", margin.top)
      .attr("width", innerWidth)
      .attr("height", innerHeight);

    // Calcular los límites del GeoJSON
    const bounds = getBounds(geoJsonData);
    const [[x0, y0], [x1, y1]] = bounds;

    // Crear escalas
    const xScale = d3.scaleLinear().domain([x0, x1]).range([0, innerWidth]);
    const yScale = d3.scaleLinear().domain([y1, y0]).range([0, innerHeight]);

    // Crear el mapa de calor
    const heatmapPoints = heatmapData.map(d => [xScale(d.lng), yScale(d.lat), d.value]);
    const contours = d3.contourDensity()
      .x(d => d[0])
      .y(d => d[1])
      .weight(d => d[2])
      .size([innerWidth, innerHeight])
      .bandwidth(40) // Ajustar el ancho de banda para una mejor distribución
      .thresholds(30)
      (heatmapPoints);

    // Heatmap color scale (verde es mejor, rojo es peor)
    const heatmapColorScale = d3.scaleSequential(d3.interpolateRdYlGn)
      .domain([0, d3.max(contours, d => d.value)]);

    g.append("g")
      .attr("fill", "none")
      .attr("stroke", "none")
      .selectAll("path")
      .data(contours)
      .join("path")
      .attr("fill", d => heatmapColorScale(d.value))
      .attr("d", d3.geoPath())
      .attr("opacity", 0.7);

    // Añadir leyenda
    const legendWidth = 20;
    const legendHeight = innerHeight / 2;
    const dBmDomain = [-100, -40];
    const legendColorScale = d3.scaleSequential(d3.interpolateRdYlGn).domain(dBmDomain);
    const legendScale = d3.scaleLinear().domain(dBmDomain).range([legendHeight, 0]);

    const legend = svg.append("g")
      .attr("transform", `translate(${width - margin.right + 40},${margin.top + innerHeight / 4})`);

    const legendGradient = legend.append("defs")
      .append("linearGradient")
      .attr("id", "legend-gradient")
      .attr("x1", "0%")
      .attr("y1", "100%")
      .attr("x2", "0%")
      .attr("y2", "0%");

    legendGradient.selectAll("stop")
      .data(d3.range(dBmDomain[0], dBmDomain[1], (dBmDomain[1] - dBmDomain[0]) / 10))
      .enter().append("stop")
      .attr("offset", (d, i) => `${(i / 9) * 100}%`)
      .attr("stop-color", d => legendColorScale(d));

    legend.append("rect")
      .attr("width", legendWidth)
      .attr("height", legendHeight)
      .style("fill", "url(#legend-gradient)");

    legend.append("text")
      .attr("x", legendWidth / 2)
      .attr("y", -10)
      .attr("text-anchor", "middle")
      .attr("font-size", "12px")
      .attr("font-weight", "bold")
      .text("Nivel de señal (dBm)");

    const legendAxis = d3.axisRight(legendScale)
      .tickSize(legendWidth)
      .ticks(5)
      .tickFormat(d3.format("d"));

    legend.append("g")
      .call(legendAxis)
      .select(".domain").remove();

    // Dibujar el contorno del edificio
    geoJsonData.features.forEach(feature => {
      if (feature.geometry.type === "Polygon") {
        const points = feature.geometry.coordinates[0].map(coord =>
          `${xScale(coord[0])},${yScale(coord[1])}`
        ).join(" ");

        g.append("polygon")
          .attr("points", points)
          .attr("fill", "none")
          .attr("stroke", "black")
          .attr("stroke-width", 2);
      } else if (feature.geometry.type === "LineString") {
        const points = feature.geometry.coordinates.map(coord =>
          `${xScale(coord[0])},${yScale(coord[1])}`
        ).join(" ");

        g.append("polyline")
          .attr("points", points)
          .attr("fill", "none")
          .attr("stroke", "black")
          .attr("stroke-width", 2);
      }
    });

    // Pintar los dispositivos (onts) y sus nombres
    g.selectAll(".device")
      .data(onts)
      .enter()
      .append("g")
      .attr("class", "device")
      .each(function (d) {
        d3.select(this)
          .append("circle")
          .attr("cx", xScale(d.x))
          .attr("cy", yScale(d.y))
          .attr("r", 5)
          .attr("fill", "blue")
          .attr("stroke", "white")
          .attr("stroke-width", 1.5);

        d3.select(this)
          .append("text")
          .attr("x", xScale(d.x))
          .attr("y", yScale(d.y) - 10)
          .attr("text-anchor", "middle")
          .attr("font-size", "10px")
          .attr("fill", "black")
          .text(d.name);
      });

    legend.selectAll(".tick text")
      .attr("x", 4)
      .attr("dy", -2);
  }, [heatmapData, geoJsonData, onts, width, height, buildingImageUrl]);

  const getBounds = (geoJsonData) => {
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    geoJsonData.features.forEach(feature => {
      const coordinates = feature.geometry.type === "Polygon"
        ? feature.geometry.coordinates[0]
        : feature.geometry.coordinates;
      coordinates.forEach(coord => {
        minX = Math.min(minX, coord[0]);
        minY = Math.min(minY, coord[1]);
        maxX = Math.max(maxX, coord[0]);
        maxY = Math.max(maxY, coord[1]);
      });
    });
    return [[minX, minY], [maxX, maxY]];
  };

  return (
    <div className="bg-white shadow-lg rounded-lg p-4">
      <svg ref={svgRef} width={width} height={height}></svg>
    </div>
  );
};

export default ContourMap;