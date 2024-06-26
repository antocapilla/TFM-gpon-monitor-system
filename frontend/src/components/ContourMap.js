import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

const ContourMap = ({ receivedPower, width, height }) => {
  const svgRef = useRef();

  useEffect(() => {
    if (!receivedPower) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const margin = { top: 20, right: 20, bottom: 30, left: 40 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const x = d3.scaleLinear().domain([0, width]).range([0, innerWidth]);
    const y = d3.scaleLinear().domain([0, height]).range([innerHeight, 0]);

    const colorScale = d3.scaleSequential(d3.interpolateViridis)
      .domain(d3.extent(receivedPower.flat()));

    const contours = d3.contours()
      .size([width, height])
      .thresholds(20)
      (receivedPower.flat());

    const g = svg.append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    g.selectAll("path")
      .data(contours)
      .enter().append("path")
      .attr("d", d3.geoPath(d3.geoIdentity().scale(innerWidth / width)))
      .attr("fill", d => colorScale(d.value));

    g.append("g")
      .attr("transform", `translate(0,${innerHeight})`)
      .call(d3.axisBottom(x));

    g.append("g")
      .call(d3.axisLeft(y));

  }, [receivedPower, width, height]);

  return (
    <svg ref={svgRef} width={width} height={height}></svg>
  );
};

export default ContourMap;