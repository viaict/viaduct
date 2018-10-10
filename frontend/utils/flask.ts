interface FlaskJsGlue {
    url_for: (route: string, params: object ) => string;
}

declare var Flask: FlaskJsGlue;

export default Flask;