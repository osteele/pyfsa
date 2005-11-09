<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:h="http://www.w3.org/1999/xhtml" 
                xmlns="http://www.w3.org/1999/xhtml"
                exclude-result-prefixes="h"
                version="1.0">
  
  <xsl:output method="html"
              omit-xml-declaration="yes"/>
  
  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="h:title">
    <xsl:copy>
      <xsl:apply-templates select="//h:h1[not(preceding::h:h1)]//text()"/>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="h:div[@class='document']">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <div class="nav">
        <ul>
          <li><a href="http://osteele.com/software/python/fsa/">Home</a></li>
          <li><a href="http://osteele.com/sources/FSA-1.0.zip">Download</a></li>
          <li>Module Documentation
        <ul>
          <li><a href="FSA.html">FSA</a></li>
          <li><a href="FSChartParser.html">FSChartParser</a></li>
          <li><a href="reCompiler.html">reCompiler</a></li>
        </ul></li>
        </ul>
      </div>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="h:h1[not(preceding::h:h1)]" priority="1">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>      
  </xsl:template>
  
  <xsl:template match="h:h1|h:h2|h:h3|h:h4|h:h5">
    <xsl:element name="h{1+substring(local-name(), 2)}"
                 xmlns="http://www.w3.org/1999/xhtml"
                 >
      <xsl:apply-templates select="@*|node()"/>
    </xsl:element>
  </xsl:template>
</xsl:stylesheet>