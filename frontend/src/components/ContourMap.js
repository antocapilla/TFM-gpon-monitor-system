import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

const ContourMap = ({ heatmapData, geoJsonData, onts, width, height }) => {
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

    // Calcular los límites del GeoJSON
    const bounds = getBounds(geoJsonData);
    const [[x0, y0], [x1, y1]] = bounds;

    // Crear escalas
    const xScale = d3.scaleLinear().domain([x0, x1]).range([0, innerWidth]);
    const yScale = d3.scaleLinear().domain([y1, y0]).range([0, innerHeight]);

    // Crear el mapa de calor
    const minValue = d3.min(heatmapData, d => d.value);
    const maxValue = d3.max(heatmapData, d => d.value);

    const colorScale = d3.scaleSequential(d3.interpolateRdYlGn)
      .domain([minValue, maxValue]);

    // Crear un mapa de calor usando rect elements
    const cellWidth = innerWidth / Math.sqrt(heatmapData.length);
    const cellHeight = innerHeight / Math.sqrt(heatmapData.length);

    g.selectAll(".heat-cell")
      .data(heatmapData)
      .enter()
      .append("rect")
      .attr("class", "heat-cell")
      .attr("x", d => xScale(d.lng))
      .attr("y", d => yScale(d.lat))
      .attr("width", cellWidth)
      .attr("height", cellHeight)
      .attr("fill", d => colorScale(d.value))
      .attr("opacity", 0.7);

    // Añadir leyenda
    const legendWidth = 20;
    const legendHeight = innerHeight / 2;
    const legendScale = d3.scaleLinear()
      .domain(colorScale.domain())
      .range([legendHeight, 0]);

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
      .data(colorScale.ticks().map((t, i, n) => ({ offset: `${100*i/n.length}%`, color: colorScale(t) })))
      .enter().append("stop")
      .attr("offset", d => d.offset)
      .attr("stop-color", d => d.color);

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
      .tickFormat(d3.format(".2f"));

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
      .join("g")
      .attr("class", "device")
      .each(function(d) {
        d3.select(this)
          .append("circle")
          .attr("cx", xScale(d.x))
          .attr("cy", yScale(d.y))
          .attr("r", 6)
          .attr("fill", "blue")
          .attr("stroke", "white")
          .attr("stroke-width", 2);

        d3.select(this)
          .append("text")
          .attr("x", xScale(d.x))
          .attr("y", yScale(d.y) - 10)
          .attr("text-anchor", "middle")
          .attr("font-size", "10px")
          .attr("fill", "black")
          .text(d.serial);
      });

  }, [heatmapData, geoJsonData, onts, width, height]);

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