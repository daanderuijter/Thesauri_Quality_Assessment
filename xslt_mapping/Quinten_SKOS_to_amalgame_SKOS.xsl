<?xml version="1.0" encoding="UTF-8"?>
<!-- Conversion file for converting library thesaurus MARC format to SKOS -->
<xsl:stylesheet 
    version="2.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:skos="http://www.w3.org/2004/02/skos/core#"
    xmlns:dct="http://purl.org/dc/terms/">
    
<xsl:output method="xml" encoding="UTF-8" indent="yes"/>

<xsl:template match="rdf:RDF">
    <rdf:RDF>
        <xsl:apply-templates select="skos:Concept"/>
    </rdf:RDF>
</xsl:template>

<xsl:template match="*|text()|@*">
	<xsl:copy>
		<xsl:apply-templates select="@*"/>
		<xsl:apply-templates/>
	</xsl:copy>
</xsl:template>

<xsl:template match="skos:Concept">
    <rdf:Description>
		<xsl:apply-templates select="*|text()|@*"/>
		<rdf:type rdf:resource="http://www.w3.org/2004/02/skos/core#Concept"/>
    </rdf:Description>
</xsl:template>

<xsl:template match="@rdf:about">
    <xsl:attribute name="rdf:about">
        <xsl:value-of select="."/>
    </xsl:attribute>
</xsl:template>

</xsl:stylesheet>