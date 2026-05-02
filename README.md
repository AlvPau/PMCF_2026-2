ANÁLISIS DEL COMPORTAMIENTO DE LAS GRÁFICAS Y JUSTIFICACIÓN DE LOS MÉTODOS UTILIZADOS


Integrantes: Paulina Álvarez, Vanessa Escobar, Vanessa Jiménez, Elias Santana




Como equipo se decidió analizar el comportamiento de la Banca Comercial y Corporativa JPMorgan Chase & Co. (JPM) desde el año 2010 utilizando las distintas metodologías de medición de riesgo de mercado. A continuación la justificación del comportamiento de las gráficas, así como la interpretación de los resultados.




(b) Respecto al cálculo de rendimientos diarios anormales de JPM.


Se realizaron los cálculos de la media, el sesgo y el exceso de curtosis de los rendimientos diarios, donde se encontraron tres hechos típicos de un activo financiero:


La media diaria desde el orden de 10 a la -4 resultó prácticamente cero,  esto confirma que el rendimiento esperado en un día es muy pequeño comparado con la volatilidad diaria. Esta observación lleva a omitir mu en estimaciones posteriores, debido a que sigma domina por completo a la media en horizontes cortos.


El resultado del sesgo es negativo, esto tiene sentido porque JPM es un banco con fuerte exposición a crédito y a tasas de interés, por lo  que sufre caídas más violentas que sus subidas. Sucesos como la crisis de 2008-2009, el flash crash de 2010, la caída por COVID-19 en marzo de 2020 y el episodio de Silicon Valley Bank en marzo de 2023 dejaron una cola izquierda especialmente pesada en la distribución.


El exceso de curtosis es muy alto, esto significa que las colas son mucho más gordas que las de una distribución normal. 




(c) Respecto al cálculo del VaR y ES bajo una aproximación paramétrica asumiendo una distribución normal y t-student, y bajo una aproximación histórica y Monte Carlo.


En la tabla comparativa se identifica un patrón muy consistente entre las cuatro metodologías:


Bajo una aproximación paramétrica asumiendo una distribución normal se subestima el riesgo en las colas, sobre todo al 99% de confianza. Se asume que la peor pérdida realista está a aproximadamente 2.33 desviaciones estándar.


Bajo una aproximación paramétrica asumiendo una distribución t-student se ajusta mejor, ya que incorpora los grados de libertad como parámetro adicional, lo que le permite capturar las colas pesadas. En el caso de JPM, los grados de libertad ajustados están entre 3 y 5 aproximadamente, es por esto que el VaR t-Student termina superando al normal, especialmente al 99%.


Bajo una aproximación histórica se refleja exactamente lo que pasó, sin suposiciones de distribución. En los resultados se entrega el VaR más alto al 99% porque incorpora directamente los eventos extremos de 2008 y marzo de 2020.


En Monte Carlo se dan resultados muy parecidos a lo obtenido bajo una distribución normal, esto era un resultado esperado pues se está replicando la hipótesis normal por simulación. Monte Carlo no rescata al modelo, sirve para entender que el método de simulación es tan bueno como la distribución que se le mete.




(d) Respecto a la gráfica de ganancias y pérdidas con una rolling window de 252 retornos




El VaR paramétrico representado con una línea azul punteada en la gráfica se ve mucho más suave que el resto, esto se debe a que depende solo de mu más sigma por z, así que cuando hay un shock en el mercado sigma sube de forma gradual porque está promediando los retornos de todo un año bursátil.


El VaR histórico representado con una línea naranja en la gráfica presenta escalones muy marcados, esto pasa porque es un cuantil empírico. Cuando un retorno extremo entra o sale de la ventana móvil, el cuantil salta de manera abrupta, es por esto que se ven mesetas planas seguidas de saltos repentinos, especialmente cuando los shocks de COVID o de SVB entran o salen del rango de la ventana. Esto visualiza directamente cómo la "memoria" del modelo histórico funciona.


El ES representado por una línea roja en la gráfica está siempre por debajo del VaR histórico, esto confirma una propiedad ya conocida: como el ES es el promedio de las pérdidas que ya superaron el VaR, por construcción tiene que ser siempre más extremo. 


(e) Respecto a la tabla de violaciones 


Tomando en cuenta que una buena estimación genera un porcentaje de violaciones menor al 2.5%, para identificar visualmente qué métodos están bien calibrados se decidió marcar en color verde el porcentaje de violaciones menor o igual a 2.5%, naranja entre 2.5 y 5%, y rojo si supera el 5%. Las observaciones son las siguientes:


El VaR paramétrico al 99% tiende a presentar más violaciones de las esperadas, lo cual confirma que la distribución normal subestima las colas. El ES presenta muy pocas violaciones porque es una medida más conservadora por construcción. Y el VaR histórico al 95% suele quedar cerca del 5% esperado, lo que valida que el método histórico está bien calibrado para nuestro horizonte.




(f) Respecto al VaR con volatilidad móvil 


Siguiendo la fórmula del VaR con volatilidad móvil se observa que el VaR se ensancha en periodos turbulentos como marzo de 2020 y se estrecha en periodos de calma como en el año 2017 o el periodo posterior a COVID. Este comportamiento adaptativo es lo que diferencia a esta aproximación de un VaR estático sobre toda la muestra. Al hacer el backtesting confirmamos que la calibración mejora notablemente.




Conclusiones


La conclusión a la que se llega como equipo es que para un banco como JPM, con colas pesadas y sesgo negativo, los métodos basados en distribuciones de colas gruesas (t-Student e histórico) o los métodos adaptativos (volatilidad móvil) dominan claramente al paramétrico normal estático. Por esa razón es que consideramos que el análisis combinado de las seis secciones ofrece una visión mucho más realista del riesgo de mercado de JPM que cualquier método aislado.
