<?xml version="1.0" encoding="UTF-8"?>
<!-- Conversion file for converting library thesaurus MARC format to SKOS -->
<xsl:stylesheet 
    version="2.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:skos="http://www.w3.org/2004/02/skos/core#"
    xmlns:dct="http://purl.org/dc/terms/">
    
<xsl:output method="xml" encoding="UTF-8" indent="yes"/>

<xsl:template match="collection">
    <rdf:RDF>
        <xsl:apply-templates select="record"/>
    </rdf:RDF>
</xsl:template>

<xsl:template match="record">
    <skos:Concept>
        <!-- Create identifier for concept -->
        <xsl:apply-templates select="controlfield[@tag = 001]"/>
        <!-- SKOS preferred label nl -->
        <xsl:apply-templates select="datafield[@tag = 150]"/>
        <!-- SKOS alternative label nl -->
        <xsl:apply-templates select="datafield[@tag = 450]"/>
        <!-- SKOS preferred label en -->
        <xsl:apply-templates select="datafield[@tag = 680]"/>
        <!-- SKOS broader/narrower/related -->
        <xsl:apply-templates select="datafield[@tag = 550]"/>
        <!-- SKOS concept scheme -->
        <xsl:apply-templates select="datafield[@tag = 942]"/>
        <!-- dcterm created -->
        <xsl:apply-templates select="controlfield[@tag = 005]"/>
        <!-- SKOS changeNote -->
        <xsl:apply-templates select="controlfield[@tag = 008]"/>
    </skos:Concept>
</xsl:template>

<!-- Create identifier for concept -->
<xsl:template match="controlfield[@tag = 001]">
    <xsl:attribute name="rdf:about">
        <xsl:text>http://hdl.handle.net/10934/RM0001.LIBTHESAU.</xsl:text>
        <xsl:value-of select="."/>
    </xsl:attribute>
</xsl:template>

<!-- SKOS preferred label nl -->
<xsl:template match="datafield[@tag = 150]">
    <skos:prefLabel xml:lang="nl">
        <!-- this particular symbol (ō, U+014D) raised an error in skosify -->
		<!-- to my knowledge xslt currently doesn't support a regex to remove non-ascii characters -->
		<!-- <xsl:value-of select="subfield"/> -->
        <xsl:value-of select="replace(subfield, 'ō', ' ')"/>
    </skos:prefLabel>
</xsl:template>

<!-- SKOS alternative label nl -->
<xsl:template match="datafield[@tag = 450]">
    <skos:altLabel xml:lang="nl">
        <xsl:value-of select="subfield"/>
    </skos:altLabel>
</xsl:template>

<!-- SKOS preferred label en -->
<xsl:template match="datafield[@tag = 680]">
    <!-- we only want the tags that start with 'Vertaling: '-->
    <xsl:if test="starts-with(subfield,'Vertaling: ')">
        <skos:prefLabel xml:lang="en">
            <!-- however, we do need to remove 'Vertaling: ' from the string -->
            <xsl:value-of select="substring-after(subfield,'Vertaling: ')"/>
        </skos:prefLabel>
    </xsl:if>
</xsl:template>

<!-- SKOS broader/narrower/related -->
<xsl:template match="datafield[@tag = 550]">
    <!-- SKOS broader -->
    <!-- if <subfield> containing 'code="w"' has value 'g', the tag is broader -->
    <xsl:apply-templates select="subfield[@code = 'w'][. = 'g']"/>
    <!-- SKOS narrower -->
    <!-- if <subfield> containing 'code="w"' has value 'h', the tag is narrower -->
    <xsl:apply-templates select="subfield[@code = 'w'][. = 'h']"/>
    <!-- if there is no <subfield> with the attribute 'code="w"', the tag is related -->
    <!-- TODO: somehow apply this requirement to a template without conflicting with other templates -->
    <xsl:if test="not(subfield[@code = 'w'])">
        <xsl:if test="subfield[@code = '0']">
			<skos:related>
				<!-- if there is a 0 code, we want to link this to an rdf:resource -->
                <xsl:apply-templates select="subfield[@code = '0']"/>
			</skos:related>
		</xsl:if>
    </xsl:if>
</xsl:template>

<!-- SKOS broader -->
<xsl:template match="subfield[@code = 'w'][. = 'g']">
	<xsl:if test="../subfield[@code = '0']">
		<skos:broader>
			<!-- if there is a 0 code, we want to link this to an rdf:resource -->
			<xsl:apply-templates select="../subfield[@code = '0']"/>
		</skos:broader>
	</xsl:if>
</xsl:template>

<!-- SKOS narrower -->
<xsl:template match="subfield[@code = 'w'][. = 'h']">
	<xsl:if test="../subfield[@code = '0']">
		<skos:narrower>
			<!-- if there is a 0 code, we want to link this to an rdf:resource -->
			<xsl:apply-templates select="../subfield[@code = '0']"/>
		</skos:narrower>
	</xsl:if>
</xsl:template>

<!-- BNR identifier -->
<xsl:template match="subfield[@code = '0']">
    <xsl:attribute name="rdf:resource">
        <!-- Create handle identifier for b/n/r concept -->
        <xsl:text>http://hdl.handle.net/10934/RM0001.LIBTHESAU.</xsl:text>
        <!-- NL-AmRIJ seems to commonly be replaced by NLAmRIJ -->
		<!-- sometime there are spaces in this field that aren't supposed to be there (29 counts) -->
        <xsl:value-of select="normalize-space(substring-after(.,'(NL-AmRIJ)'))"/>
        <xsl:value-of select="normalize-space(substring-after(.,'(NLAmRIJ)'))"/>
    </xsl:attribute>
</xsl:template>

<!-- SKOS concept scheme -->
<xsl:template match="datafield[@tag = 942]">
    <skos:inScheme>
        <xsl:attribute name="rdf:resource">
            <!-- Create identifier for concept -->
            <xsl:text>http://hdl.handle.net/10934/RM0001.SCHEME.</xsl:text>
            <xsl:value-of select="subfield"/>
        </xsl:attribute>
    </skos:inScheme>
</xsl:template>

<!-- dcterm created -->
<xsl:template match="controlfield[@tag = 008]">
	<dct:created>
		<!-- apply regex to match string representation with the collection thesaurus -->
		<!-- MARC date: 'yymmdd' followed by some trail string -->
		<!-- SKOS date: 'yyyy-mm-dd' -->
		<!-- first we check whether the first 'y' is in [0,1] or not, from this we can infer the century -->
		<xsl:choose>
			<!-- if the first 'y' is in [0,1] we insert '20' -->
			<xsl:when test="substring(.,1,1) = '0' or substring(.,1,1) = '1'">
				<!-- replace() applies a regex substitution, normalize-space(substring-before()) removes the trail string -->
				<xsl:value-of select="normalize-space(substring-before(replace(., '([01]\d)(\d\d)(\d\d)' , '20$1-$2-$3'), '|'))"/>
			</xsl:when>
			<!-- if the first 'y' is not in [0,1] we insert '19' -->
			<xsl:otherwise>
				<!-- replace() applies a regex substitution, normalize-space(substring-before()) removes the trail string -->
				<xsl:value-of select="normalize-space(substring-before(replace(., '([2-9]\d)(\d\d)(\d\d)' , '19$1-$2-$3'), '|'))"/>
			</xsl:otherwise>
		</xsl:choose>
	</dct:created>
</xsl:template>

<!-- SKOS change note -->
<xsl:template match="controlfield[@tag = 005]">
    <skos:changeNote>
        <!-- add a blank node -->
        <rdf:Description>
            <dct:modified>
				<!-- apply regex to match string representation with the collection thesaurus -->
                <!-- SKOS date: 'yyyy-mm-dd' -->
				<!-- replace() applies a regex substitution, substring selects the first 10 characters -->
				<xsl:value-of select="substring(replace(., '(\d\d\d\d)(\d\d)(\d\d)' , '$1-$2-$3'),1,10)"/>
            </dct:modified>
        </rdf:Description>
    </skos:changeNote>
</xsl:template>

</xsl:stylesheet>