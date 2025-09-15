function [parameters] = reader_DDS(parameters)
%**************************************************************************
% функция считывает .dds файл
% Входные данные:
%     - parameters   - параметры режима
%
% Выходные данные:
%     - t_ZI    - массив времени
%     - ZI      - образ ЗИ (в соответствии с параметрами dds)
%
%**************************************************************************
% 
% Мосолов С.
% v 1.1: 30 November 2016

  try

   fid = fopen( [parameters.path,parameters.name_file,'.dds'], 'rb');  

% Считывание struct DDS_HDR //размер = 16 байт 
% // Структура описания заголовка записи 
% Struct gHeader // Размер = 16 байт
% {
% Ulong Sig1 = 0x55AA0F0F; // +0 - Код сигнатуры 1 (константа )
% Ulong Sig2 = 0xFF00CAAC; // +4 - Код сигнатуры 2 (константа )
% Ushort Version; // +8 - Код версии данных (старший байт – номер версии = {0..255},
%                                         младший байт – номер подверсии = {0..255})
% Ushort Type; // +10 - Код типа данных записи - Таблица 5
% ULong Size; // +12 Ushort Type; // +10 - Код типа данных записи (размер REC_DATA)
% }
%
%------------------------------------------------------------------------- 
%     dm_log('----------------------------------------------------------------')
%     dm_log('Считываем заголовок...')
%     dm_log(' ')
% 
% Считывание struct DDS_HDR //размер = 16 байт 
    [a,count] = fread(fid,[1,1],'ulong');     sig1 = a;
    [a,count] = fread(fid,[1,1],'ulong');     sig2 = a;
    [a,count] = fread(fid,[1,1],'ushort');    version = a;
    [a,count] = fread(fid,[1,1],'ushort');    rec_type = a;
    [a,count] = fread(fid,[1,1],'ulong');     size_file = a;
    
%     dm_log(['Сигнатура 1 - ',num2str(sig1,'%X'),'h']);
%     dm_log(['Сигнатура 2 - ',num2str(sig2,'%X'),'h']);
%     dm_log(['Версия      - ',num2str(version,'%u')]);
%     dm_log(['Тип записи  - ',num2str(rec_type,'%X'),'h']);
%     dm_log(['Размер      - ',num2str(size_file,'%u'), ' байт']);
%     
%     dm_log(' ')
%     dm_log('Ok!')
%     dm_log(' ')
%     dm_log('----------------------------------------------------------------')
    
% ------------------------------------------------------------------------- 
% Считывание struct gPRM_ZI //размер = 16+128=144 байта
% согласно файлу Гидра_DDS.9
%
% // Описание структуры gPRM_ZI
% struct gPRM_ZI // Размер структуры = 16+128 = 144 байта 
% {
% Ushort CodeZI; 		// +0 (2 байта) Код ЗИ
% Uchar Mode;           // +2 ( 1 байт) 
% Uchar Mode1;          // +3 (1 байт) - Резерв = 0
% Ushort TimeZ; 		// +4 ( 2 байта)
% Ulong NumPrd; 		// +6 ( 4 байта )
% Ushort TimeR; 		// +10 (2 байта)
% Ushort TimeI; 		// +12 (2 байта)
% Ushort CRC;           // +14 (2 байта) – Всего 16 байт
% 
% Ulong Prm0;           // +16 (4 байта)
% Ulong Prm1;           // +20 (4 байта)
% Uchar Ver;            // +24 (1 байт)
% Uchar Type;           // +25 (1 байт)
% Wchar Name_RU[ 20 ];	// +26 (40 байт) – строка UNICODE – до 19 символов
% Wchar Name_EN[ 20 ];	// +66 (40 байт) – строка UNICODE – до 19 символов
% Double StartFreq; 	// +106 (8 байт)
% Double EndFreq;       // +114 (8 байт)
% Double TimeZI;		// +122 (8 байт)
% Double Fs;            // +130 (8 байт)
% Uchar SampleType; 	// +138 (1 байт)
% Uchar Rzv2;           // +139 (1 байт) - резерв = 0
% Ushort NumCC;         // +140 (2 байт)
% Uchar Rzv3[ 2 ];      // +142 (2 байт) - резерв = 0
% }
%--------------------------------------------------------------------------    
%     dm_log('Считываем параметры ЗИ...')
%     dm_log(' ')

    [a,count] = fread(fid,[1,1],'ushort');    Code_ZI = a;
    [a,count] = fread(fid,[1,1],'uchar');     Mode = a;
    [a,count] = fread(fid,[1,1],'uchar');     Mode1 = a;
    [a,count] = fread(fid,[1,1],'ushort');    TimeZ = a;
    [a,count] = fread(fid,[1,1],'ulong');     NumPrd = a;
    [a,count] = fread(fid,[1,1],'ushort');    TimeR = a+3;
    [a,count] = fread(fid,[1,1],'ushort');    TimeI = a+2;
    [a,count] = fread(fid,[1,1],'ushort');    CRC = a;
    
%     dm_log(['Код ЗИ     - ',num2str(Code_ZI,'%u')]);
%     dm_log(['Mode       - ',num2str(Mode,'%hX'),'h']);
%     dm_log(['TimeZ      - ',num2str(TimeZ,'%u')]);
%     dm_log(['NumPrd     - ',num2str(NumPrd,'%u')]);
%     dm_log(['TimeR      - ',num2str(TimeR,'%u')]);
%     dm_log(['TimeI      - ',num2str(TimeI,'%u')]);
%     dm_log(['CRC        - ',num2str(CRC,'%X')]);
     
    [a,count] = fread(fid,[1,1],'ulong');     Prm0 = a;     
    [a,count] = fread(fid,[1,1],'ulong');     Prm1 = a;   
    [a,count] = fread(fid,[1,1],'char');      Ver = a;
    [a,count] = fread(fid,[1,1],'char');      Type = a;
    [a,count] = fread(fid,[1,20],'ushort');   Name_RU = native2unicode(a);
    [a,count] = fread(fid,[1,20],'ushort');   Name_EN = native2unicode(a);
    [a,count] = fread(fid,[1,1],'double');    StartFreq = a; 
    [a,count] = fread(fid,[1,1],'double');    EndFreq = a;
    [a,count] = fread(fid,[1,1],'double');    TimeZI = a;
    [a,count] = fread(fid,[1,1],'double');    Fs = a;
    [a,count] = fread(fid,[1,1],'char');      SampleType = a;
    [a,count] = fread(fid,[1,1],'char');      Rzv2 = a;
    [a,count] = fread(fid,[1,1],'uint16');    NumCC = a;
    [a,count] = fread(fid,[1,2],'char');      Rzv3 = a;
    
%     dm_log(['Prm0       - ',num2str(Prm0,'%u')]);
%     dm_log(['Prm1       - ',num2str(Prm1,'%u')]);
%     dm_log(['Ver        - ',num2str(Ver,'%u')]);
%     dm_log(['Type       - ',num2str(Type,'%u')]);
%     dm_log(['Name_RU    - ',Name_RU]);
%     dm_log(['Name_EN    - ',Name_EN]);
%     dm_log(['StartFreq  - ',num2str(StartFreq/1000,'%3.3f'),' кГц']);
%     dm_log(['EndFreq    - ',num2str(EndFreq/1000,'%3.3f'),' кГц']);
%     dm_log(['TimeZI     - ',num2str(TimeZI*10^6,'%3.3f'),' мкс']);
%     dm_log(['FSample    - ',num2str(Fs/1000,'%4.4f'),' кГц']);
%     dm_log(['SampleType - ',num2str(SampleType,'%X'),'h']);
%     dm_log(['NumCC      - ',num2str(NumCC,'%u')]);
%     dm_log(' ')
%     dm_log('Ok!')
%     dm_log(' ')
%     dm_log('----------------------------------------------------------------')

    parameters.signal_data_dig = [];

    Mode0 = bitget(Mode,8:-1:1);
    Mode0 = bin2dec(num2str(Mode0));

%     dm_log('Считываем команды управления (КУ) генератором...')

    if Mode < 4  


        % считываем команды управления и формируем ЗИ ---------------------

        Polarity = 1;
        NumTic = 0;
            if Mode0 == 0  % Mode = 0, версия _v1
                TimePrd  = fread(fid,[1,1],'uint16');
                for k = 1:NumCC-1
                    DeltaRep = fread(fid,[1,1],'uint16');
                    Delta = bitget(DeltaRep,5:-1:1);
                    Sign = bitget(DeltaRep,6);
                    Rep = bitget(DeltaRep,16:-1:7);
                    Delta = bin2dec(num2str(Delta));
                    Rep = bin2dec(num2str(Rep));
                    if Sign == 0
                        Sign = -1;
                    end
                    for n = 1:Rep
                        parameters.signal_data_dig = ...
                               [parameters.signal_data_dig ...
                                sin(pi*TimePrd^-1*(1:2*TimePrd))];
                    end
                    TimePrd = TimePrd + Sign*Delta;
                end
            else
                for k = 1:NumCC/4
                    T0 = fread(fid,[1,1],'uint8')+2;
                    T1 = fread(fid,[1,1],'uint8')+2;
                    T2 = fread(fid,[1,1],'uint8')+2;
                    T3 = fread(fid,[1,1],'uint8')+2;
                    CC_3 = fread(fid,[1,1],'uint16');
                    Last = bitget(CC_3,16);
                    Polarity_b = bitget(CC_3,15);
                    EnaTe = bitget(CC_3,14);
                    ModeD = bitget(CC_3,12:-1:9);
                    tmp = bitget(CC_3,8:-1:1);
                    Rep_L = bin2dec(num2str(tmp))+1;
                    Rep_H = fread(fid,[1,1],'ushort');
                    ModeD = bin2dec(num2str(ModeD));
                     if Polarity_b == 1
                        Polarity = 1;
                     else
                        Polarity = -1;
                     end
                     if EnaTe == 1
                         Rep = Rep_L;
                         Num_Te = Rep_H+1;
                     else
                         Rep = 256*Rep_H + Rep_L;
                         Num_Te = 0;
                     end
                     switch ModeD 
                         case 0  % без ШИМ
                            D = [0 1 1 1 1 1 1];
                         case 1  % ШИМ
                            D = [0 1 0 1 0 1 0];
                         case 2 % гасящие импульсы
                            D = [0 0 0 1 0 0 0];
                         case 3 % ~сверхдлинная пауза
                            D = [0 0 0 0 0 0 0];
                         otherwise
                             dm_log('Ошибка!!! не понятная команда в КУ')
                             break
                     end
                     for n = 1:Rep
                            parameters.signal_data_dig = [parameters.signal_data_dig ...
                                  Polarity*D(1)*(ones(1,T0)) ...
                                  Polarity*D(2)*(ones(1,T1)) ...
                                  Polarity*D(3)*(ones(1,T2)) ...
                                  Polarity*D(4)*(ones(1,T3)) ...
                                  Polarity*D(5)*(ones(1,T2)) ...
                                  Polarity*D(6)*(ones(1,T1)) ...
                                  Polarity*D(7)*(ones(1,T0))];
                        TimePrd = 2*T0 + 2*T1 + 2*T2 + T3;
                        NumTic = NumTic + TimePrd;
                        Polarity = -Polarity;
                     end
                     parameters.signal_data_dig = [parameters.signal_data_dig zeros(1,Num_Te)];
                 
%                      if k == 1
%                          dm_log('----------------------------------------------------------------');
%                          dm_log('номер СС |  T0 |  T1 |  T2 |  T3 |   T | NTf | Polarity | Last');
%                          dm_log('----------------------------------------------------------------');
%                      end
     
%                      fprintf('% 8u | % 3u | % 3u | % 3u | % 3u | % 3u | % 3u | % 8u | % 3u\n', ...
%                              k, ...
%                              T0, ...
%                              T1, ...
%                              T2, ...
%                              T3, ...
%                              TimePrd, ...
%                              Rep, ...
%                              Polarity_b, ...
%                              Last);
                        
                     if Last == 1
                         break
                     end
                     
                end
            end
%             dm_log('----------------------------------------------------------------');
%             dm_log(['                           Tзи = ',num2str(1e6*NumTic*parameters.Tclk,'%6.3f'),' мкс']);
            parameters.signal_time_dig = 0:parameters.Tclk:(size(parameters.signal_data_dig,2)-1)*parameters.Tclk;
                                
    elseif Mode == 4
        
        %% моделируем работу GCHIRP (считаем количество тиков в фазах сигнала)
               
        [a,count] = fread(fid,[1,1],'ulong');    GCHIRP.M1 = a;
        [a,count] = fread(fid,[1,1],'ulong');    GCHIRP.N = a + 1;
        [a,count] = fread(fid,[1,1],'ulong');    GCHIRP.NumPrd = a + 1;
        [a,count] = fread(fid,[1,1],'ulong');    GCHIRP.TimeZ = a;
        [a,count] = fread(fid,[1,1],'int8');     GCHIRP.ModeAccumM = a;
        
        GCHIRP.fclk = parameters.fclk;
        GCHIRP.Tclk = parameters.Tclk;
        GCHIRP.timeZI = parameters.timeZI;
        GCHIRP.J = parameters.J;
        GCHIRP.timeZ = parameters.timeZ;
        GCHIRP.signal_time = parameters.signal_time;
        GCHIRP.modeAccumM = parameters.modeAccumM;
  
        [ GCHIRP ] = simulation_GCHIRP( GCHIRP );
 
        parameters.signal_time_dig = GCHIRP.signal_time_packaging;
        parameters.signal_data_dig = GCHIRP.signal_packaging;
        
    elseif Mode == 5 
        % Формирование сигнала по КУ
        dm_log('   Формируем сигнал по командам управления') 
        [ parameters ] = repackag_CC2signal( parameters );

        parameters.signal_time_dig = parameters.signal_time_packaging;
        parameters.signal_data_dig = parameters.signal_packaging;
        
    elseif Mode == 6
        
        %% моделируем работу GCHIRP (считаем количество тиков в фазах сигнала)
               
        [a,count] = fread(fid,[1,1],'ulong');    GCHIRP.M1 = a;
        [a,count] = fread(fid,[1,1],'ulong');    GCHIRP.N = a + 1;
        [a,count] = fread(fid,[1,1],'ulong');    GCHIRP.NumPrd = a + 1;
        [a,count] = fread(fid,[1,1],'ulong');    GCHIRP.TimeZ = a;
        [a,count] = fread(fid,[1,1],'int8');     GCHIRP.ModeAccumM = a;
        
        GCHIRP.fclk = parameters.fclk;
        GCHIRP.Tclk = parameters.Tclk;
        GCHIRP.timeZI = parameters.timeZI;
        GCHIRP.J = parameters.J;
        GCHIRP.timeZ = parameters.timeZ;
        GCHIRP.signal_time = parameters.signal_time;
        GCHIRP.modeAccumM = parameters.modeAccumM;
  
        [ GCHIRP ] = simulation_GCHIRP( GCHIRP );
 
        parameters.signal_time_dig = GCHIRP.signal_time_packaging;
        parameters.signal_data_dig = GCHIRP.signal_packaging;
        
    elseif Mode == 7
        % Формирование сигнала по КУ
        dm_log('   Формируем сигнал по командам управления') 
        [ parameters ] = repackag_CC2signal( parameters );

        parameters.signal_time_dig = parameters.signal_time_packaging;
        parameters.signal_data_dig = parameters.signal_packaging;
    else
        dm_log('Error!!!......Заданный режим генератора не поддерживается!');
        return
    end

    fclose(fid);
    %%
    
  catch err
   rethrow(err);
  end 
end