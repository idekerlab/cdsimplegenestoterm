FROM continuumio/miniconda3

RUN mkdir /tmp/cdsimple
COPY dist/*.whl /tmp/cdsimple/
COPY data.gmt /tmp/cdsimple/

RUN pip install /tmp/cdsimple/cdsimplegenestoterm*whl

RUN /opt/conda/bin/cdsimplegenestotermcmd.py --savedb /tmp/cdsimplegenestoterm.pickle /tmp/cdsimple/data.gmt

RUN rm -rf /tmp/cdsimple


ENTRYPOINT ["/opt/conda/bin/cdsimplegenestotermcmd.py"]
CMD ["--help"]
